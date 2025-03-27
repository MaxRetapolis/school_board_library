# School Board Documents Usage DB Generator

## Commands
- Setup: `pip install -e .` or `python -m pip install -r requirements.txt`
- Run Generator: `python src/usage_db_generator.py`
- Run Queries: `python src/query_usage_db.py --query [top_documents|daily_summary|document_detail]`
- Run Tests: `python -m unittest tests/test_usage_db_generator.py`
- Run Everything: `./run.sh`

## Code Style Guidelines
- **Imports**: Standard library first, third-party next, local modules last
- **Typing**: Document parameter and return types in docstrings
- **Naming**: snake_case for functions/variables, CamelCase for classes
- **Documentation**: Use triple-quoted docstrings for modules and functions
- **Error Handling**: Use specific exception handling with proper validation
- **Functions**: Design atomic, reusable functions with single responsibility
- **Performance**: Use batch operations and list comprehensions where appropriate

## Architecture
The system follows an atomic, composable architecture with five main functional blocks:
1. Meeting date generation
2. Document metadata creation
3. User simulation (bots and people)
4. Usage data generation
5. SQLite database storage