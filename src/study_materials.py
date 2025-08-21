"""
Study Materials Manager - Learning resources and techniques
Compatible with Python 3.8-3.12
"""

import json
import os
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import random

class StudyMaterialsManager:
    """Manages study materials, resources, and learning techniques."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.materials_dir = self.data_dir / "materials"
        
        # Ensure directories exist
        self.materials_dir.mkdir(parents=True, exist_ok=True)
        
        # Materials data
        self.materials_file = self.materials_dir / "materials.json"
        
        # Default study materials
        self.default_materials = self.get_default_materials()
        
        # Load existing materials
        self.materials = self.load_materials()
        
    def get_default_materials(self) -> Dict[str, Any]:
        """Get default study materials and techniques."""
        return {
            "quick_links": [
                {
                    "name": "Khan Academy",
                    "url": "https://www.khanacademy.org/",
                    "category": "Learning Platform",
                    "description": "Free online courses and tutorials"
                },
                {
                    "name": "Coursera",
                    "url": "https://www.coursera.org/",
                    "category": "Learning Platform", 
                    "description": "University-level online courses"
                },
                {
                    "name": "Pomodoro Timer",
                    "url": "https://pomofocus.io/",
                    "category": "Productivity",
                    "description": "Online Pomodoro technique timer"
                },
                {
                    "name": "Forest",
                    "url": "https://www.forestapp.cc/",
                    "category": "Focus App",
                    "description": "Stay focused and plant virtual trees"
                },
                {
                    "name": "Quizlet",
                    "url": "https://quizlet.com/",
                    "category": "Study Tools",
                    "description": "Create and study with flashcards"
                }
            ],
            "study_techniques": [
                {
                    "name": "Pomodoro Technique",
                    "description": "Break work into 25-minute intervals with short breaks",
                    "steps": [
                        "Choose a task to work on",
                        "Set timer for 25 minutes",
                        "Work on the task until timer rings",
                        "Take a 5-minute break",
                        "After 4 pomodoros, take a longer break (15-30 minutes)"
                    ],
                    "benefits": "Improves focus, reduces mental fatigue, increases productivity"
                },
                {
                    "name": "Active Recall",
                    "description": "Test yourself on material rather than re-reading",
                    "steps": [
                        "Read through material once",
                        "Close your notes/textbook",
                        "Write down everything you remember",
                        "Check your notes for accuracy",
                        "Focus on areas you missed"
                    ],
                    "benefits": "Strengthens memory, identifies knowledge gaps, improves retention"
                },
                {
                    "name": "Spaced Repetition",
                    "description": "Review material at increasing intervals",
                    "steps": [
                        "Learn new material",
                        "Review after 1 day",
                        "Review after 3 days", 
                        "Review after 1 week",
                        "Review after 2 weeks",
                        "Review after 1 month"
                    ],
                    "benefits": "Long-term retention, efficient use of time, prevents forgetting"
                },
                {
                    "name": "Feynman Technique", 
                    "description": "Explain concepts in simple terms to test understanding",
                    "steps": [
                        "Choose a concept you want to learn",
                        "Write it out in plain English as if teaching someone else",
                        "Identify gaps in your explanation", 
                        "Go back to source material to fill gaps",
                        "Simplify your explanation even further"
                    ],
                    "benefits": "Deep understanding, identifies misconceptions, simplifies complex topics"
                },
                {
                    "name": "Mind Mapping",
                    "description": "Create visual representations of information",
                    "steps": [
                        "Start with main topic in center",
                        "Add major subtopics as branches",
                        "Add details to each subtopic",
                        "Use colors and symbols",
                        "Connect related concepts"
                    ],
                    "benefits": "Visual learning, shows relationships, aids memory"
                }
            ],
            "productivity_tips": [
                "Remove distractions from your study environment",
                "Use the Pomodoro Technique for better focus",
                "Take regular breaks to maintain concentration", 
                "Stay hydrated and maintain good posture",
                "Study in a well-lit, comfortable space",
                "Use background music or white noise if helpful",
                "Set specific, achievable study goals",
                "Reward yourself after completing study sessions",
                "Review material before sleeping for better retention",
                "Practice active recall instead of passive re-reading",
                "Use spaced repetition for long-term learning",
                "Teach concepts to others to test understanding",
                "Create a consistent study schedule",
                "Break large tasks into smaller, manageable chunks"
            ],
            "motivational_quotes": [
                "The expert in anything was once a beginner.",
                "Success is the sum of small efforts repeated day in and day out.",
                "Don't watch the clock; do what it does. Keep going.",
                "The only way to learn mathematics is to do mathematics.",
                "Education is not preparation for life; education is life itself.",
                "Learning never exhausts the mind.",
                "Knowledge is power. Information is liberating.",
                "The more that you read, the more things you will know.",
                "Study hard what interests you the most in the most undisciplined way.",
                "Intelligence is the ability to adapt to change.",
                "The beautiful thing about learning is nobody can take it away from you.",
                "Education is the most powerful weapon which you can use to change the world.",
                "Live as if you were to die tomorrow. Learn as if you were to live forever.",
                "An investment in knowledge pays the best interest.",
                "The capacity to learn is a gift; the ability to learn is a skill; the willingness to learn is a choice."
            ]
        }
        
    def load_materials(self) -> Dict[str, Any]:
        """Load study materials from file."""
        try:
            if self.materials_file.exists():
                with open(self.materials_file, 'r', encoding='utf-8') as f:
                    loaded_materials = json.load(f)
                    
                # Merge with defaults to ensure all categories exist
                materials = self.default_materials.copy()
                for key, value in loaded_materials.items():
                    if key in materials and isinstance(value, list):
                        materials[key].extend(value)
                    else:
                        materials[key] = value
                        
                return materials
        except Exception as e:
            print(f"Error loading materials: {e}")
            
        return self.default_materials.copy()
        
    def save_materials(self):
        """Save current materials to file."""
        try:
            with open(self.materials_file, 'w', encoding='utf-8') as f:
                json.dump(self.materials, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving materials: {e}")
            
    def add_quick_link(self, name: str, url: str, category: str = "Custom", 
                      description: str = "") -> bool:
        """Add a new quick link."""
        try:
            new_link = {
                "name": name,
                "url": url,
                "category": category,
                "description": description,
                "added_date": datetime.now().isoformat()
            }
            
            # Check if link already exists
            for link in self.materials["quick_links"]:
                if link["name"] == name or link["url"] == url:
                    return False
                    
            self.materials["quick_links"].append(new_link)
            self.save_materials()
            return True
            
        except Exception as e:
            print(f"Error adding quick link: {e}")
            return False
            
    def remove_quick_link(self, name: str) -> bool:
        """Remove a quick link by name."""
        try:
            original_length = len(self.materials["quick_links"])
            self.materials["quick_links"] = [
                link for link in self.materials["quick_links"] 
                if link["name"] != name
            ]
            
            if len(self.materials["quick_links"]) < original_length:
                self.save_materials()
                return True
            return False
            
        except Exception as e:
            print(f"Error removing quick link: {e}")
            return False
            
    def open_quick_link(self, name: str) -> bool:
        """Open a quick link in the default web browser."""
        try:
            for link in self.materials["quick_links"]:
                if link["name"] == name:
                    webbrowser.open(link["url"])
                    return True
            return False
            
        except Exception as e:
            print(f"Error opening quick link: {e}")
            return False
            
    def get_categories(self) -> List[str]:
        """Get list of quick link categories."""
        categories = set()
        for link in self.materials["quick_links"]:
            categories.add(link.get("category", "Uncategorized"))
        return sorted(list(categories))
        
    def get_daily_motivation(self) -> str:
        """Get a random motivational quote."""
        quotes = self.materials.get("motivational_quotes", [])
        if quotes:
            return random.choice(quotes)
        return "Stay focused and keep learning!"
        
    def get_study_technique(self, name: str) -> Optional[Dict[str, Any]]:
        """Get details of a specific study technique."""
        for technique in self.materials["study_techniques"]:
            if technique["name"].lower() == name.lower():
                return technique
        return None
        
    def get_productivity_tip(self) -> str:
        """Get a random productivity tip."""
        tips = self.materials.get("productivity_tips", [])
        if tips:
            return random.choice(tips)
        return "Take regular breaks to maintain focus!"
        
    def search_materials(self, query: str) -> Dict[str, List[Dict[str, Any]]]:
        """Search through all materials for a query."""
        query = query.lower()
        results = {
            "quick_links": [],
            "study_techniques": [],
            "tips": []
        }
        
        # Search quick links
        for link in self.materials["quick_links"]:
            if (query in link["name"].lower() or 
                query in link.get("description", "").lower() or
                query in link.get("category", "").lower()):
                results["quick_links"].append(link)
                
        # Search study techniques
        for technique in self.materials["study_techniques"]:
            if (query in technique["name"].lower() or
                query in technique.get("description", "").lower()):
                results["study_techniques"].append(technique)
                
        # Search productivity tips
        for tip in self.materials["productivity_tips"]:
            if query in tip.lower():
                results["tips"].append({"tip": tip})
                
        return results
        
    def export_materials(self, file_path: str) -> bool:
        """Export materials to a file."""
        try:
            export_data = {
                "export_date": datetime.now().isoformat(),
                "materials": self.materials
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            return True
            
        except Exception as e:
            print(f"Error exporting materials: {e}")
            return False
            
    def import_materials(self, file_path: str) -> bool:
        """Import materials from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
                
            if "materials" in import_data:
                imported_materials = import_data["materials"]
                
                # Merge imported materials with existing ones
                for key, value in imported_materials.items():
                    if key in self.materials and isinstance(value, list):
                        # Add new items, avoiding duplicates
                        for item in value:
                            if item not in self.materials[key]:
                                self.materials[key].append(item)
                    else:
                        self.materials[key] = value
                        
                self.save_materials()
                return True
                
        except Exception as e:
            print(f"Error importing materials: {e}")
            
        return False
