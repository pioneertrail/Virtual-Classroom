import json
from student_profile import StudentProfile

def test_profile():
    # Create a new student profile
    student = StudentProfile("test123", "Alex")
    
    # Test adding interactions
    student.add_interaction(
        "What's a planet?",
        "A planet is a large object that orbits around a star.",
        "high"
    )
    
    # Test updating learning style
    student.update_learning_style("visual", "kinesthetic", 0.85)
    
    # Test adding interests
    student.add_interest("space")
    student.add_interest("robots")
    
    # Print profile summary
    print("\nProfile Summary:")
    print(json.dumps(student.get_profile_summary(), indent=2))
    
    # Print full profile
    print("\nFull Profile:")
    print(json.dumps(student.profile, indent=2))

if __name__ == "__main__":
    test_profile() 