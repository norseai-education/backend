from langchain_core.tools import tool
from langchain_core.tools import StructuredTool
from src.services.math_engine import MathEngine
import src.services.rag_service as rag_service
from pydantic import BaseModel, Field, model_validator
import json
import random
from src.utils import logging
from src.utils import knowledge_info

# Configure logging
logger = logging.set_logger(__name__)

math_engine_instance = MathEngine()


class MathContextInput(BaseModel):
    student_id: str = Field(description="The student's unique id")
    query: str = Field(description="The mathematics context you are searching for")

    @model_validator(mode="before")
    @classmethod
    def fix_double_serialization(cls, values):
        if (
            isinstance(values, dict)
            and "student_id" in values
            and isinstance(values["student_id"], str)
            and values["student_id"].strip().startswith("{")
        ):
            try:
                parsed = json.loads(values["student_id"])
                return {**values, **parsed}
            except json.JSONDecodeError:
                pass
        return values



class GetArchivedInput(BaseModel):
    student_id: str = Field(description="The student's unique id")
    query: str = Field(description="The text you are trying to get context for")

    @model_validator(mode="before")
    @classmethod
    def fix_double_serialization(cls, values):
        if (
            isinstance(values, dict)
            and "student_id" in values
            and isinstance(values["student_id"], str)
            and values["student_id"].strip().startswith("{")
        ):
            try:
                parsed = json.loads(values["student_id"])
                return {**values, **parsed}
            except json.JSONDecodeError:
                pass
        return values

# class GetProblemInput(BaseModel):
#     subject: str = Field(description="The subject you want the problem to cover")
#     difficulty: int = Field(description="The problem difficulty from 1-8")

    # @model_validator(mode="before")
    # @classmethod
    # def fix_double_serialization(cls, values):
    #     # If values is a string that looks like JSON, parse it
    #     if isinstance(values, str) and values.strip().startswith("{"):
    #         try:
    #             parsed = json.loads(values)
    #             return parsed
    #         except json.JSONDecodeError:
    #             pass
        
    #     # If values is a dict, check if any field contains JSON strings
    #     if isinstance(values, dict):
    #         result = {}
    #         for key, value in values.items():
    #             if isinstance(value, str) and value.strip().startswith("{"):
    #                 try:
    #                     parsed = json.loads(value)
    #                     # Only merge if the parsed JSON contains the expected fields
    #                     if all(field in parsed for field in ["difficulty", "concepts"]):
    #                         return parsed
    #                     else:
    #                         result[key] = value
    #                 except json.JSONDecodeError:
    #                     result[key] = value
    #             else:
    #                 result[key] = value
    #         return result
        
    #     return values

# class CheckConceptsInput(BaseModel):
#     concepts: dict[str, list[str]] = Field(description="The concepts you want to check")

@tool
def math_engine(expression: str) -> str:
    """Math engine for difficult expressions and large computations using SymPy"""
    try:
        logging.log("Using math_engine tool...", logger, 2)
        logging.log(f"Tool inputs: \n{expression},{type(expression)}", logger, 2)
        # Clean input
        expr = expression.strip()
        
        # Handle different types of mathematical operations
        if expr.startswith(('factor(', 'gcd(', 'lcm(', 'factorial(', 'binomial(', 'prime(')):
            return math_engine_instance._handle_special_functions(expr)
        
        if 'mod' in expr.lower():
            return math_engine_instance._handle_modular_arithmetic(expr)
        
        if ';' in expr or '\n' in expr or (',' in expr and '=' in expr):
            return math_engine_instance._solve_system_of_equations(expr)
    
        if '=' in expr and not any(op in expr for op in ['==', '<=', '>=', '!=']):
            return math_engine_instance._solve_equation(expr)
        
        # evaluate as general expression
        return math_engine_instance._evaluate_expression(expr)
        
    except Exception as e:
        return f"Error: {str(e)}"
    
@tool
def check_concepts(input_data: str) -> str:
    """Verify if concepts are in the Concepts List"""
    input_data = json.loads(input_data)
    concepts = input_data.get('concepts')
    try:
        logging.log("Using check_concepts tool... ", logger, 2)
        logging.log(f"Tool inputs: \n{concepts},{type(concepts)}", logger, 2)
        bad_concepts = []
        for concept in concepts:
            if concept.lower() not in knowledge_info.amc8_concepts:
                bad_concepts.append(concept)

        if bad_concepts:
            return f"These concepts: {bad_concepts} are not in the Concepts List"
        else:
            return "All concepts are in the concepts list"
        
    except Exception as e:
        return f"Error: {str(e)}"
    
# check_concepts_structured = StructuredTool.from_function(
#     func=check_concepts,
#     name="check_concepts",
#     description="Verify if concepts are in the Concepts List",
#     args_schema=CheckConceptsInput,
# )
    
def get_math_context(input_data: MathContextInput) -> str:
    """Get further context for the student input if needed."""
    input_data = json.loads(input_data)

    logging.log("Using get_math_context tool...", logger, 2)
    logging.log(f"Tool inputs: {input_data},{type(input_data)}", logger, 2)

    student_id = input_data.get('student_id')
    query = input_data.get('query')
    math_related_db = rag_service.MathRelatedDB()
    math_context = math_related_db.retrieve(query, n_results=1, metadata_filter = {"student_id": str(student_id)})
    return math_context

get_math_context_structured = StructuredTool.from_function(
    func=get_math_context,
    name="get_math_context",
    description="get further context for the student input if needed",
    args_schema=MathContextInput,
)


# @tool(args_schema = GetArchivedInput)
def get_archived(input_data: GetArchivedInput):
    """get conversation history for more context"""
    input_data = json.loads(input_data)
    
    logging.log("Using get_archived tool...", logger, 2)
    logging.log(f"Tool inputs: {input_data},{type(input_data)}", logger, 2)

    student_id = input_data.get('student_id')
    query = input_data.get('query')
    archived_db = rag_service.ArchivedConversationHistory()
    archived = archived_db.retrieve(query, 3, {"student_id": str(student_id)})
    return archived

get_archived_structured = StructuredTool.from_function(
    func=get_archived,
    name="get_archived",
    description="get further context for the student input if needed",
    args_schema=GetArchivedInput,
)

@tool
def get_problem(problem_input: str) -> str:
    """retrieve a problem to give to the student"""
    input_data = json.loads(problem_input)

    problem_id = ""
    problem_text = ""
    solution = ""

    subject = input_data.get('subject')
    difficulty = input_data.get('difficulty')
    difficulty_range = [difficulty, difficulty+1 if difficulty != 5 else difficulty-1]
    problem_db = rag_service.ProblemDB()
    problem, metadata, ids = problem_db.retrieve(subject, n_results=15)
    valid_problems = []
    for data in metadata:
        concepts_list = data['concepts'].split(',')
        if data['difficulty'] in difficulty_range and subject.lower() in [concept.lower() for concept in concepts_list]:
            valid = metadata.index(data)
            valid_problems.append(valid)

    if valid_problems:
        place = random.choice(valid_problems)
        problem_id = ids[place]
        problem_text = problem[place]
        solution = metadata[place]['solution']
    else:
        problem_id = ids[0]
        problem_text = problem[0]
        solution = metadata[0]['solution']

    return f"problem_id: {problem_id}\nProblem text: {problem_text}\nSolution: {solution}"

# get_problem_structured = StructuredTool.from_function(
#     func=get_problem,
#     name="get_problem",
#     description="retrieve a problem to give to the student based on subject, difficulty, and concepts",
#     args_schema=GetProblemInput,
# )
