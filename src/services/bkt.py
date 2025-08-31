from backend.src.services.state import State
from backend.src.utils import knowledge_info
from backend.src.utils import logging

# Configure logging
logger = logging.set_logger(__name__)

"""
Bayesian Knowledge Tracing (BKT) Implementation with Configurable Sensitivity

This implementation allows you to control how sensitive the algorithm is to individual
correct/incorrect responses. The key parameters are:

BKT Parameters:
- P_will_learn: Probability of learning a concept in a single interaction
  * Higher values = faster learning, more sensitive
  * Lower values = slower learning, less sensitive
  * Range: 0.01 to 0.1 (0.03 is conservative, 0.08 is aggressive)

- P_slip: Probability of making a mistake when you know the concept
  * Higher values = more forgiving of mistakes
  * Lower values = less forgiving of mistakes
  * Range: 0.05 to 0.15 (0.08 is balanced)

- P_guess: Probability of getting correct by guessing when you don't know
  * Higher values = more suspicious of correct answers
  * Lower values = more trusting of correct answers
  * Range: 0.1 to 0.3 (0.15 is balanced)

- damping_factor: How much of the calculated change to actually apply
  * 1.0 = full change (most sensitive)
  * 0.6 = 60% of change (moderate sensitivity)
  * 0.3 = 30% of change (least sensitive)

Example usage for different sensitivity levels:

# Very conservative (least sensitive)
bkt = BayesianKnowledgeTracing(
    list_of_learning_obj=your_list,
    p_will_learn=0.02,
    p_slip=0.1,
    p_guess=0.2,
    damping_factor=0.4
)

# Balanced (moderate sensitivity)
bkt = BayesianKnowledgeTracing(
    list_of_learning_obj=your_list,
    p_will_learn=0.03,
    p_slip=0.08,
    p_guess=0.15,
    damping_factor=0.6
)

# Aggressive (most sensitive)
bkt = BayesianKnowledgeTracing(
    list_of_learning_obj=your_list,
    p_will_learn=0.08,
    p_slip=0.05,
    p_guess=0.1,
    damping_factor=1.0
)
"""

class BayesianKnowledgeTracing():
    def __init__(self, list_of_learning_obj: list[str],
                 p_will_learn: float = 0.03,
                 p_slip: float = 0.08,
                 p_guess: float = 0.15):
        self.list_of_learning_obj = list_of_learning_obj
        self.P_will_learn = p_will_learn
        self.P_slip = p_slip
        self.P_guess = p_guess

    def bkt_algorithm(self, grade, cur_graph, damping_factor):
        logging.log(f"Used damping factor of {damping_factor}", logger, 2)
        # Process each graded concept
        for concept, result in grade.items():
            # Get current P_known value and P_init
            P_known = cur_graph[concept]

            
            # Determine if the answer was correct
            is_correct = (result.lower() == "correct")
            
            if is_correct:
                # Student answered correctly
                P_learned = (P_known * (1-self.P_slip))/(P_known * (1-self.P_slip) + (1-P_known) * self.P_guess)
                
                # Apply damping to reduce sensitivity
                raw_update = P_learned + (1-P_learned) * self.P_will_learn
                updated_probability = P_known + damping_factor * (raw_update - P_known)
                    
            else:
                # Student answered incorrectly
                P_learned = (P_known * self.P_slip)/(P_known * self.P_slip + (1-P_known) * (1-self.P_guess))
                
                # Apply damping to reduce sensitivity
                raw_update = P_learned + (1-P_learned) * self.P_will_learn
                updated_probability = P_known + damping_factor * (raw_update - P_known)
            
            # Ensure probability stays within [0, 1] bounds
            updated_probability = max(0.0, min(1.0, updated_probability))
            
            # Update both the current graph and the p_init values for next time
            cur_graph[concept] = updated_probability
        
        return cur_graph

    def update_learning_obj(self, cur_learning_obj, init_learning_obj, updated_graph, learning_status):
        logging.log("Updating learning objectives and learning status...", logger, 2)
        # Get current learning objective index
        try:
            cur_index = self.list_of_learning_obj.index(cur_learning_obj)
        except ValueError:
            # If current learning objective not found, start from beginning
            cur_index = 0
            cur_learning_obj = self.list_of_learning_obj[0]
        
        # Rule 1: Check if any concept BEFORE current learning concept is below 0.75
        concepts_behind = []
        for i in range(cur_index):
            concept = self.list_of_learning_obj[i]
            if updated_graph.get(concept, 0.0) < 0.75:
                concepts_behind.append((i, concept))
        
        if concepts_behind:
            
            # Go back to the earliest concept that's below 0.75
            earliest_behind = min(concepts_behind, key=lambda x: x[0])
            logging.log(f"Concept behind found: \n{earliest_behind}", logger, 2)

            return {
                "cur_learning_objective": earliest_behind[1],
                "init_learning_objective": init_learning_obj,  # Preserve original objective
                "learning_status": "behind",
                "bkt_graph": updated_graph,
                "lesson_state": {
                    'START_LESSON': 'Done', 
                    'CONCEPT_INTRODUCTION': 'In Progress', 
                    'GIVE_EASIER_PROBLEM': 'Not Done', 
                    'PROBLEM_WALKTHROUGH': 'Not Done', 
                    'GIVE_HARDER_PROBLEM': 'Not Done', 
                    'END_LESSON': 'Not Done'
                }
            }
        
        # Rule 2: If nothing before is < 0.75, check if current concept mastery > 0.95
        current_mastery = updated_graph.get(cur_learning_obj, 0.0)
        
        if current_mastery > 0.95:
            logging.log("Current mastery is above 0.95!", logger, 2)
            # Check if we're still behind (need to return to original objective)
            current_status = learning_status
            
            if current_status == "behind":
                # We were behind, check if we should return to original objective
                original_index = self.list_of_learning_obj.index(init_learning_obj)
                
                # Check if there are still concepts before the original objective that are < 0.75
                remaining_behind = []
                for i in range(original_index):
                    concept = self.list_of_learning_obj[i]
                    if updated_graph.get(concept, 0.0) < 0.75:
                        remaining_behind.append((i, concept))
                
                if remaining_behind:
                    # Still have concepts below 0.75 before original objective
                    # Go to the earliest one that needs work
                    earliest_remaining = min(remaining_behind, key=lambda x: x[0])
                    return {
                        "cur_learning_objective": earliest_remaining[1],
                        "init_learning_objective": init_learning_obj,
                        "learning_status": "behind",
                        "bkt_graph": updated_graph,
                        "lesson_state": {
                            'START_LESSON': 'Done', 
                            'CONCEPT_INTRODUCTION': 'In Progress', 
                            'GIVE_EASIER_PROBLEM': 'Not Done', 
                            'PROBLEM_WALKTHROUGH': 'Not Done', 
                            'GIVE_HARDER_PROBLEM': 'Not Done', 
                            'END_LESSON': 'Not Done'
                        }
                    }
                else:
                    # All concepts before original objective are now >= 0.75
                    # Return to original objective and set to steady
                    logging.log("Returning to original objective!", logger, 2)
                    return {
                        "cur_learning_objective": init_learning_obj,
                        "init_learning_objective": init_learning_obj,
                        "learning_status": "steady",
                        "bkt_graph": updated_graph
                    }
            
            # Normal forward progression (not behind scenario)
            next_index = cur_index + 1
            if next_index < len(self.list_of_learning_obj):
                next_obj = self.list_of_learning_obj[next_index]
                logging.log("Moving ahead to next objective!", logger, 2)
                return {
                    "cur_learning_objective": next_obj,
                    "init_learning_objective": init_learning_obj,
                    "learning_status": "ahead",
                    "bkt_graph": updated_graph,
                    "lesson_state": {
                        'START_LESSON': 'Done',
                        'CHECK': 'In Progress', 
                        'CONCEPT_INTRODUCTION': 'Not Done', 
                        'GIVE_EASIER_PROBLEM': 'Not Done', 
                        'PROBLEM_WALKTHROUGH': 'Not Done', 
                        'GIVE_HARDER_PROBLEM': 'Not Done', 
                        'END_LESSON': 'Not Done'
                    }
                }
            else:
                # Completed all learning objectives
                return {
                    "cur_learning_objective": "Completed Unit",
                    "init_learning_objective": init_learning_obj,
                    "learning_status": "ahead",
                    "bkt_graph": updated_graph
                }
        
        # Rule 3: Current concept mastery <= 0.95 and nothing before is < 0.75
        # Stay on current concept with steady status
        return {
            "cur_learning_objective": cur_learning_obj,
            "init_learning_objective": init_learning_obj,
            "learning_status": "steady",
            "bkt_graph": updated_graph
        }

    def get_mastery(self, updated_graph):
        cur_mastery = []
        for key, value in updated_graph.items():
            if value > 0.9:
                cur_mastery.append(key)
        if cur_mastery:
            return cur_mastery
        else:
            return ["No mastery, assume basic knowledge"]


    def build_node(self, state: State):
        logging.log(f"Current state: \n{state}", logger, 2)
        logging.log("Going through BKT node...", logger, 2)
        grade = state.get("evaluator_grade", {})
        cur_learning_obj = state.get("cur_learning_objective")
        init_learning_obj = state.get("init_learning_objective")
        cur_graph = state.get("bkt_graph", knowledge_info.amc8_knowledge_graph)
        learning_status = state.get("learning_status")
        lesson_state = state.get("lesson_state")

        logging.log(f"Current bkt graph: \n{cur_graph}", logger, 2)
        # Update the knowledge graph using BKT algorithm based on lesson state
        cur_state = ''
        for key, value in lesson_state.items():
            if value.lower() == 'in progress':
                cur_state = key

        # change damping factor based on current state
        if cur_state.lower() == 'start_lesson' or cur_state.lower() == 'end_lesson':
            updated_graph = self.bkt_algorithm(grade, cur_graph, 0.3)
        elif cur_state.lower() == 'concept_introduction' or cur_state.lower() == 'problem_walkthrough':
            updated_graph = self.bkt_algorithm(grade, cur_graph, 0.6)
        elif cur_state.lower() == 'give_easier_problem' or cur_state.lower() == 'give_harder_problem':
            updated_graph = self.bkt_algorithm(grade, cur_graph, 0.8)
        else:
            updated_graph = self.bkt_algorithm(grade, cur_graph, 0.5)


        logging.log(f"Updated bkt graph: \n{updated_graph}", logger, 2)
        cur_mastery = self.get_mastery(updated_graph)
        logging.log(f"Student's current knowledge: {cur_mastery}", logger, 2)
        node = self.update_learning_obj(cur_learning_obj, init_learning_obj, updated_graph, learning_status)
        # Add mastery information to the node
        node["cur_mastery"] = cur_mastery

        return node
        

        
            
