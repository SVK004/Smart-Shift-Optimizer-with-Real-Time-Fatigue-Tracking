Features Implemented
-> Accepts input for employees and tasks.
-> Processes tasks under time and resource constraints.
-> Allocates suitable employees for each task and updates their records accordingly.

Future Improvements
-> Currently uses an in-memory data store; plan to switch to a persistent MySQL database.
-> Should validate and prevent illogical time jumps (e.g., task time before last recorded shift)