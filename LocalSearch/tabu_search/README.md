# First glance at Tabu Search
Tabu search is a metaheuristic algorithm that can be used to solve optimization problems, including scheduling problems. It works by maintaining a list of "tabu" moves that are not allowed to be made, and using this list to guide the search towards promising areas of the solution space.

To apply tabu search to the scheduling problem you described, you could start by defining a representation for the solution space. For example, you might represent a schedule as a list of tuples, with each tuple containing the subject, room, day, and section for a particular exam.

Next, you would need to define a set of moves that can be made to transform one solution into another. For example, a move might involve swapping the schedule for two subjects, or moving a subject to a different day or time slot.

Then, you would need to define an objective function that evaluates the quality of a given schedule. This could be the total number of days used, or some other measure of the schedule's fitness.

Finally, you would implement the tabu search algorithm itself, using the moves and objective function you defined to guide the search towards better solutions.

One thing to keep in mind is that tabu search can get stuck in local optima, so it may not always find the absolute best solution to the problem. However, it can be a effective way to find good solutions quickly, and it can be especially useful for problems where the solution space is very large or the objective function is complex.


# Tabu Search in Details
Here are the steps involved in the tabu search algorithm:

Initialize the current solution and the best solution found so far. The current solution is typically set to an initial schedule, which can be created using a variety of methods such as randomly generating a schedule or using a heuristic to construct a schedule. The best solution is initially set to the same value as the current solution.

Iterate for a maximum number of iterations. In each iteration, do the following:

1. Find a neighbor of the current solution by making one or more moves. A move is an operation that transforms the current solution into a new solution by adding, deleting, or modifying one or more elements. Examples of moves include swapping the time slots of two subjects, moving a subject to a different time slot, or adding a subject to an empty time slot.
2. Evaluate the quality of the neighbor using an objective function. The objective function measures the goodness of a solution and returns a value that can be used to compare different solutions. For example, the objective function might return the number of days required to schedule all the exams, or the number of students that need to be rescheduled due to conflicts.
3. If the neighbor is better than the current solution, update the current solution to be the neighbor.
4. If the neighbor is better than the best solution found so far, update the best solution to be the neighbor.
5. Add the moves made to the tabu list. The tabu list is a list of moves that are not allowed to be made in the next few iterations. This helps to prevent the search from getting stuck in a local optimal solution by prohibiting moves that lead to solutions that were previously explored.

After the maximum number of iterations has been reached, return the best solution found as the result of the tabu search.
