# Final Project

[![Web App CI](https://github.com/swe-students-fall2025/5-final-daynight-jam/actions/workflows/web.yml/badge.svg)](
https://github.com/swe-students-fall2025/5-final-daynight-jam/actions/workflows/web.yml)[![mongodb CI](https://github.com/swe-students-fall2025/5-final-daynight-jam/actions/workflows/mongodb-ci.yml/badge.svg)](
https://github.com/swe-students-fall2025/5-final-daynight-jam/actions/workflows/mongodb-ci.yml)[![Docker CI](https://github.com/swe-students-fall2025/5-final-daynight-jam/actions/workflows/docker-cicd.yml/badge.svg)](
https://github.com/swe-students-fall2025/5-final-daynight-jam/actions/workflows/docker-cicd.yml)

[Live Deployment on Digital Ocean](https://daynight-jam-f8voz.ondigitalocean.app/)

## Introduction
Recipe Jam is a collaborative recipe recommendation and exploration platform designed to help users discover meals based on their available ingredients, dietary preferences, and personal constraints. By combining user input with an intelligent recommendation engine, Recipe Jam provides an interactive and personalized cooking experience from ingredient selection to final recipe guidance.

Users can input ingredients they currently have, specify dietary restrictions, allergies, preferred cuisines, and available kitchen tools. Based on this information, Recipe Jam generates relevant recipe suggestions, complete with required ingredients, step-by-step cooking instructions, recommended tools, and possible substitutions. This allows users to reduce food waste, save time, and experiment confidently in the kitchen.

Additionally, Recipe Jam helps users plan ahead by tracking previously generated recipes and automatically creating shopping lists for missing ingredients. Through an intuitive interface and data-driven recommendations, Recipe Jam aims to simplify home cooking while encouraging creativity and flexibility in everyday meals.

## Features
* User Authentication 
Secure signup, login, and logout to provide a personalized cooking experience.

* Ingredient & Kitchen Setup
Specify what’s available in your kitchen to tailor recipe recommendations:
   * Ingredients you have on hand
   * Kitchen tools you own (e.g., oven, air fryer, blender)
   * Ingredients to avoid due to allergies or preferences

* Recipe Recommendations
Browse recipes generated from your inputs, with detailed cooking guidance:
   * Complete ingredient lists
   * Step-by-step cooking instructions
   * Required kitchen tools
   * Suggested substitutions for ingredients or cookware

* Shopping List Management
Automatically build and manage a shopping list based on selected recipes:
   * Add ingredients from recipes
   * Track completed and remaining items
   * Manually add or remove items as needed

## Class Members
Haonan Cai [Dexter](https://github.com/TogawaSaki0214)
YI-KAI HUANG [Daniel-H](https://github.com/DANIELX-X)
Leon Lian [lastteatime](https://github.com/ll5373128)
John Ovalles [John](https://github.com/jmo7728)

## Setup and Installation

### Setup

1. Navigate to the project root directory:

```bash
cd /path/to/5-final-daynight-jam/web
```

2. Create a virtual environment:
```bash
python3 -m venv venv
```

3. Activate the virtual environment:
```bash
source venv/bin/activate
```

4. Create a virtual environment:
```bash
pip install -r requirements.txt
```

5. Run the application:
```bash
python run.py
```

The application will be available at: (http://localhost:8000)

### Docker Setup
To run the application using Docker Compose:
```bash
docker-compose up
```

## Deployment

The CI/CD pipeline and env should just reference these secrets configured in this GitHub repository's settings:
| Secret | Description |
|--------|------------|
| DOCKERHUB_USERNAME   | Docker Hub username |
| DOCKERHUB_TOKEN  | Docker Hub personal access token |
| DIGITALOCEAN_ACCESS_TOKEN | Digital Ocean API token |
| MONGO_URI | URI for mongodb |
| FLASK_SECRET_KEY | Key for Flask App |
| OPENAI_API_KEY | API key for ml client |