# COMP0034 Coursework 1 2023/24
COMP0034 Coursework 1 starter repository

## Instructions to configure and run the app

1. Fork the repository and cloned it to an IDE
2. Create and activate a virtual environment
3. Install the requirements `pip install -r requirements.txt`
4. Run the app `flask --app src run --debug`
5. Open a browser and go to http://127.0.0.1:5000/items, http://127.0.0.1:5000/items/8 and http://127.0.0.1:5000/comments which return a list of all items, data for item of id=8, and a list of all comments respectively
6. Stop the app using `CTRL+C`
7. Check that there is a folder called `instance` containing `database.sqlite`
8. Configure the IDE to support running pytests
9. Install the application code `pip install -e .`
10. Run tests in the IDE

More information for this coursework is shown in `./comp0034-coursework1.md`