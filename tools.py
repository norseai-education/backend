from langchain_core.tools import tool
from langchain_core.tools import StructuredTool
from math_engine import MathEngine
import models
import database
from pydantic import BaseModel, Field, model_validator
import json
import utils

# Configure logging
logger = utils.set_logger(__name__)

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

class GetProblemInput(BaseModel):
    subject: str = Field(description="The main subject you want the problem to cover")
    difficulty: int = Field(description="The problem difficulty from 1-8")
    concepts: list[str] = Field(description="The specific concepts you want the problem to cover")

    @model_validator(mode="before")
    @classmethod
    def fix_double_serialization(cls, values):
        # If values is a string that looks like JSON, parse it
        if isinstance(values, str) and values.strip().startswith("{"):
            try:
                parsed = json.loads(values)
                return parsed
            except json.JSONDecodeError:
                pass
        
        # If values is a dict, check if any field contains JSON strings
        if isinstance(values, dict):
            result = {}
            for key, value in values.items():
                if isinstance(value, str) and value.strip().startswith("{"):
                    try:
                        parsed = json.loads(value)
                        # Only merge if the parsed JSON contains the expected fields
                        if all(field in parsed for field in ["subject", "difficulty", "concepts"]):
                            return parsed
                        else:
                            result[key] = value
                    except json.JSONDecodeError:
                        result[key] = value
                else:
                    result[key] = value
            return result
        
        return values

@tool
def math_engine(expression: str) -> str:
    """Math engine for difficult expressions and large computations using SymPy"""
    try:
        utils.log("Using math_engine tool...", logger, 2)
        utils.log(f"Tool inputs: \n{expression},{type(expression)}", logger, 2)
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
    
def get_math_context(input_data: MathContextInput) -> str:
    """Get further context for the student input if needed."""
    input_data = json.loads(input_data)

    utils.log("Using get_math_context tool...", logger, 2)
    utils.log(f"Tool inputs: {input_data},{type(input_data)}", logger, 2)

    student_id = input_data.get('student_id')
    query = input_data.get('query')
    math_related_db = database.MathRelatedDB(models.embedding_model)
    math_related_client = math_related_db.connect_to_db()
    math_related_collection = math_related_db.get_collection(math_related_client, "math_related_db")
    math_context = math_related_db.retrieve(math_related_collection, query, n_results=1, metadata_filter = {"student_id": student_id})
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
    
    utils.log("Using get_archived tool...", logger, 2)
    utils.log(f"Tool inputs: {input_data},{type(input_data)}", logger, 2)

    student_id = input_data.get('student_id')
    query = input_data.get('query')
    archived_db = database.ArchivedConversationHistory(models.embedding_model)
    archived_db_client = archived_db.connect_to_db()
    archived_db_collection = archived_db.get_collection(archived_db_client, "conversation_history")
    archived = archived_db.retrieve(archived_db_collection, query, 1, {"student_id": student_id})
    return archived

get_archived_structured = StructuredTool.from_function(
    func=get_archived,
    name="get_archived",
    description="get further context for the student input if needed",
    args_schema=GetArchivedInput,
)

def get_problem(input_data: GetProblemInput):
    """retrieve a problem to give to the student"""
    input_data = json.loads(input_data)
    
    utils.log("Using get_problem tool...", logger, 2)
    utils.log(f"Tool inputs: {input_data},{type(input_data)}", logger, 2)

    subject = input_data.get('subject')
    difficulty = input_data.get('difficulty')
    concepts = input_data.get('concepts')
    problem_db = database.ProblemDB(models.embedding_model)
    problem_db_client = problem_db.connect_to_db()
    problem_db_collection = problem_db.get_collection(problem_db_client, "problem_db")
    problem = problem_db.retrieve(problem_db_collection, subject, {"difficulty": difficulty, "concepts": concepts}, n_results=1)
    return problem

get_problem_structured = StructuredTool.from_function(
    func=get_problem,
    name="get_problem",
    description="retrieve a problem to give to the student based on subject, difficulty, and concepts",
    args_schema=GetProblemInput,
)