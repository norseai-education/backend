#!/usr/bin/env python3
"""
Fake Assessment Data Generator for NorseAI

This script generates fake assessment data to simulate the AMC8 assessment system.
It creates:
1. 25 math problems with solutions
2. Sample student assessment results
"""

import random
from datetime import datetime
import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.MongoDBHandler import MongoDBHandler
from src.config.settings import settings

class FakeAssessmentData:
    def __init__(self):
        self.db = MongoDBHandler(settings.mongodb_url)
        self.db.connect('amc8_database')

    def generate_problems(self):
        """Generate 25 fake AMC8-style math problems"""

        problems = [
            {
                "problem_number": 1,
                "problem": "If x + 3 = 7, what is the value of x?",
                "correct_answer": "4",
                "solution": "Subtract 3 from both sides: x + 3 - 3 = 7 - 3 → x = 4"
            },
            {
                "problem_number": 2,
                "problem": "What is 25% of 80?",
                "correct_answer": "20",
                "solution": "25% = 0.25, so 0.25 × 80 = 20"
            },
            {
                "problem_number": 3,
                "problem": "Solve for x: 2x + 5 = 13",
                "correct_answer": "4",
                "solution": "Subtract 5: 2x = 8, then divide by 2: x = 4"
            },
            {
                "problem_number": 4,
                "problem": "What is the area of a rectangle with length 6 and width 4?",
                "correct_answer": "24",
                "solution": "Area = length × width = 6 × 4 = 24"
            },
            {
                "problem_number": 5,
                "problem": "If a triangle has angles 30°, 60°, and 90°, what type of triangle is it?",
                "correct_answer": "right triangle",
                "solution": "A triangle with a 90° angle is a right triangle"
            },
            {
                "problem_number": 6,
                "problem": "Simplify: 2 + 3 × 4",
                "correct_answer": "14",
                "solution": "Following order of operations (PEMDAS), multiply first: 3 × 4 = 12, then add: 2 + 12 = 14"
            },
            {
                "problem_number": 7,
                "problem": "What is the perimeter of a square with side length 5?",
                "correct_answer": "20",
                "solution": "Perimeter = 4 × side = 4 × 5 = 20"
            },
            {
                "problem_number": 8,
                "problem": "Solve: x² = 16",
                "correct_answer": "4 or -4",
                "solution": "Square root of 16 is ±4"
            },
            {
                "problem_number": 9,
                "problem": "What is 40% of 150?",
                "correct_answer": "60",
                "solution": "40% = 0.4, so 0.4 × 150 = 60"
            },
            {
                "problem_number": 10,
                "problem": "If 3x = 12, what is x?",
                "correct_answer": "4",
                "solution": "Divide both sides by 3: x = 12 ÷ 3 = 4"
            },
            {
                "problem_number": 11,
                "problem": "What is the volume of a cube with side length 3?",
                "correct_answer": "27",
                "solution": "Volume = side³ = 3³ = 27"
            },
            {
                "problem_number": 12,
                "problem": "Solve: 5x - 2 = 18",
                "correct_answer": "4",
                "solution": "Add 2: 5x = 20, then divide by 5: x = 4"
            },
            {
                "problem_number": 13,
                "problem": "What is ¾ as a decimal?",
                "correct_answer": "0.75",
                "solution": "¾ = 75/100 = 0.75"
            },
            {
                "problem_number": 14,
                "problem": "Find the mean of 2, 4, 6, 8, 10",
                "correct_answer": "6",
                "solution": "Sum = 30, divide by 5 numbers: 30 ÷ 5 = 6"
            },
            {
                "problem_number": 15,
                "problem": "What is the area of a circle with radius 2? (Use π ≈ 3.14)",
                "correct_answer": "12.56",
                "solution": "Area = πr² = 3.14 × 2² = 3.14 × 4 = 12.56"
            },
            {
                "problem_number": 16,
                "problem": "Solve: x/3 = 5",
                "correct_answer": "15",
                "solution": "Multiply both sides by 3: x = 5 × 3 = 15"
            },
            {
                "problem_number": 17,
                "problem": "What is 125% of 80?",
                "correct_answer": "100",
                "solution": "125% = 1.25, so 1.25 × 80 = 100"
            },
            {
                "problem_number": 18,
                "problem": "If angle A is 45° and angle B is 45°, what is angle C in triangle ABC?",
                "correct_answer": "90°",
                "solution": "Angles in triangle sum to 180°: 45° + 45° + C = 180° → C = 90°"
            },
            {
                "problem_number": 19,
                "problem": "Simplify: 2² + 3²",
                "correct_answer": "13",
                "solution": "2² = 4, 3² = 9, so 4 + 9 = 13"
            },
            {
                "problem_number": 20,
                "problem": "What is the probability of rolling a 6 on a fair die?",
                "correct_answer": "1/6",
                "solution": "There are 6 equally likely outcomes, only 1 is a 6"
            },
            {
                "problem_number": 21,
                "problem": "Solve: 4x + 2 = 10",
                "correct_answer": "2",
                "solution": "Subtract 2: 4x = 8, then divide by 4: x = 2"
            },
            {
                "problem_number": 22,
                "problem": "What is the circumference of a circle with diameter 8? (Use π ≈ 3.14)",
                "correct_answer": "25.12",
                "solution": "Circumference = π × diameter = 3.14 × 8 = 25.12"
            },
            {
                "problem_number": 23,
                "problem": "Find the median of 1, 3, 5, 7, 9",
                "correct_answer": "5",
                "solution": "Middle value when numbers are sorted: 5"
            },
            {
                "problem_number": 24,
                "problem": "What is 60% of 200?",
                "correct_answer": "120",
                "solution": "60% = 0.6, so 0.6 × 200 = 120"
            },
            {
                "problem_number": 25,
                "problem": "If 2x = 6, what is x?",
                "correct_answer": "3",
                "solution": "Divide both sides by 2: x = 6 ÷ 2 = 3"
            }
        ]

        return problems

    def generate_student_assessment(self, student_id: int, assessment_id: str, num_correct: int = None):
        """Generate fake student assessment results"""

        # Get all problems
        problems = self.db.find_documents('problems', {}, ['_id', 'problem_number', 'correct_answer'])

        if num_correct is None:
            num_correct = random.randint(5, 20)  # Random score between 5-20 correct

        assessment_results = []
        correct_count = 0

        for problem in problems:
            # Decide if this answer should be correct
            is_correct = correct_count < num_correct
            if is_correct and random.random() < 0.8:  # 80% chance of correct answer if we need more correct
                student_answer = problem['correct_answer']
                correct_count += 1
            elif not is_correct and random.random() < 0.6:  # 60% chance of wrong answer if we have enough correct
                # Generate wrong answer
                correct = problem['correct_answer']
                if correct.isdigit():
                    wrong_answers = [str(int(correct) + random.randint(1, 5)),
                                   str(int(correct) - random.randint(1, 3)) if int(correct) > 0 else str(random.randint(1, 10))]
                    student_answer = random.choice(wrong_answers)
                else:
                    student_answer = "wrong answer"
            else:
                student_answer = problem['correct_answer']
                if is_correct:
                    correct_count += 1

            assessment_results.append({
                "student_id": student_id,
                "assessment_id": assessment_id,
                "problem_id": str(problem['_id']),
                "student_answer": student_answer,
                "time_spent_seconds": random.randint(30, 300),  # 30 seconds to 5 minutes
                "timestamp": datetime.now()
            })

        return assessment_results

    async def populate_problems(self):
        """Insert all problems into the database"""
        print("Populating problems collection...")

        # Clear existing problems
        self.db.delete_document('problems', {})

        problems = self.generate_problems()
        for problem in problems:
            await self.db.insert_document('problems', problem)

        print(f"✅ Inserted {len(problems)} problems")

    async def populate_sample_assessments(self):
        """Create sample student assessments"""
        print("Creating sample student assessments...")

        # Clear existing assessments
        self.db.delete_document('assessments', {})

        # Create assessments for 3 sample students with different skill levels
        students = [
            {"id": 1, "name": "Beginner Student", "expected_correct": 8},
            {"id": 2, "name": "Intermediate Student", "expected_correct": 15},
            {"id": 3, "name": "Advanced Student", "expected_correct": 22}
        ]

        for student in students:
            assessment_id = f"{student['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            assessment_data = self.generate_student_assessment(
                student['id'],
                assessment_id,
                student['expected_correct']
            )

            for entry in assessment_data:
                await self.db.insert_document('assessments', entry)

            print(f"✅ Created assessment for {student['name']} (ID: {student['id']}) - Expected: {student['expected_correct']}/25 correct")

    def run(self):
        """Run the complete data generation process"""
        print("🚀 Starting Fake Assessment Data Generation")
        print("=" * 50)

    async def run(self):
        """Run the complete data generation process"""
        print("🚀 Starting Fake Assessment Data Generation")
        print("=" * 50)

        try:
            await self.populate_problems()
            await self.populate_sample_assessments()

            print("=" * 50)
            print("✅ Fake assessment data generation complete!")
            print("\n📊 Generated:")
            print("   • 25 AMC8-style math problems")
            print("   • Sample assessments for 3 students")
            print("   • Beginner: ~8/25 correct")
            print("   • Intermediate: ~15/25 correct")
            print("   • Advanced: ~22/25 correct")

        except Exception as e:
            print(f"❌ Error generating fake data: {e}")
            raise

if __name__ == "__main__":
    generator = FakeAssessmentData()
    asyncio.run(generator.run())