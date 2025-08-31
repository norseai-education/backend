def convert_messages_to_dict(messages, student_id):
    """
    Converts a list of HumanMessage and AIMessage objects to a list of dictionaries.
    
    Args:
        messages: List containing HumanMessage and AIMessage objects
        
    Returns:
        List of dictionaries with 'student'/'teacher' keys and content values
    """
    result = []
    
    for message in messages:
        # Get the class name to determine message type
        message_type = message.__class__.__name__
        
        if message_type == 'HumanMessage':
            result.append({'student_id': student_id, 'role': 'student', 'content': message.content})
        elif message_type == 'AIMessage':
            result.append({'student_id': student_id, 'role': 'teacher', 'content': message.content})
    
    return result