# Code Smells

Use this reference when reviewing or refactoring PHP and you need to name a smell, judge whether it really hurts here, and pick the refactoring that removes it.

## Table of Contents

- [How to Use a Smell](#how-to-use-a-smell)
- [Bloaters](#bloaters)
- [Object-Orientation Abusers](#object-orientation-abusers)
- [Change Preventers](#change-preventers)
- [Dispensables](#dispensables)
- [Couplers](#couplers)
- [Other Smells](#other-smells)
- [Sources](#sources)

## How to Use a Smell

A code smell is "a surface indication that usually corresponds to a deeper problem in the system." It is quick to notice, and it is an indicator of a problem, not the problem itself. A smell does not always mean something is wrong: some long methods are fine, so look deeper before acting. A smell often points to a design issue that needs investigation first. For a data class, ask what behaviour belongs in it; the answer can lead to the refactoring.

A team can pick a "smell of the week" to look for and raise with senior members.

Use the groups and refactoring names below as the shared vocabulary.

## Bloaters

Code, methods or classes "that have grown so large they are hard to work with. They usually accumulate over time."

### Long Method

- **Signs:** "A method contains too many lines of code." As a rule of thumb, "any method longer than ten lines should make you start asking questions." A function above about half a dozen lines already starts to smell.
- **Why it hurts:** "The longer a method or function is, the harder it becomes to understand and maintain it." Long methods are "the perfect hiding place for unwanted duplicate code."
- **Treatment:** Extract Method. If you feel the need to comment on something inside a method, move that code into a new method; even a single line may need extraction if it requires explanation. Conditionals and loops are a good clue for extraction. When local variables or parameters get in the way, use Replace Temp with Query, Introduce Parameter Object or Preserve Whole Object; if that fails, Replace Method with Method Object. For conditionals, Decompose Conditional.
- **Extract by intention:** if you have to spend effort looking at a fragment to figure out what it does, extract it and name the function after that "what".
- **Payoff:** shorter methods are easier to understand and maintain. The cost of more methods is negligible in almost all cases.
- **Pitfalls:** "something is always being added to a method but nothing is ever taken out." Small functions only work if the names are good.

### Large Class

- **Signs:** "A class contains many fields/methods/lines of code."
- **Causes:** classes start small and bloat as the program grows. Adding a feature to an existing class is "mentally less taxing" than creating a new one.
- **Treatment:** split a class wearing too many functional hats. Extract Class when part of the behaviour can be a separate component; Extract Subclass when behaviour is implemented in different ways or used rarely; Extract Interface when clients need a list of operations.
- **Payoff:** developers no longer need to remember many attributes, and splitting often removes duplicated code.

### Primitive Obsession

- **Signs:** primitives instead of small objects for simple tasks such as currency, ranges or phone numbers; constants that encode information, such as `USER_ADMIN_ROLE = 1`; string constants used as field names in data arrays.
- **Causes:** primitives are used to "simulate" types. The problem begins when someone adds "just a field" instead of creating a class.
- **Treatment:** Replace Data Value with Object; Introduce Parameter Object or Preserve Whole Object; Replace Type Code with Class, with Subclasses, or with State/Strategy; Replace Array with Object.
- **Payoff:** "Code becomes more flexible thanks to use of objects instead of primitives." Duplicates become easier to spot.

### Long Parameter List

- **Signs:** "More than three or four parameters for a method."
- **Causes:** several algorithms merged into one method, with parameters picking the algorithm; or decoupling, where objects created in the caller are passed in as parameters.
- **Treatment:** Replace Parameter with Method Call; Preserve Whole Object; Introduce Parameter Object for parameters from different sources; let the method use data from its own object, or pass another object that supplies the data.
- **When to ignore:** "Don't get rid of parameters if doing so would cause unwanted dependency between classes."
- **Payoff:** shorter, more readable code that may reveal duplicate code.

### Data Clumps

- **Signs:** different parts of the code contain identical groups of variables, such as database connection parameters.
- **Causes:** poor program structure or "copypasta programming".
- **Test:** remove one value from the group. If the rest no longer makes sense together, it is a data clump and should become its own class.
- **Treatment:** Extract Class when the repeated data forms fields of a class; Introduce Parameter Object when the clump is passed as parameters; Preserve Whole Object; move the code that operates on these fields into the new data class.
- **When to ignore:** passing a whole object instead of its primitive values can create an undesirable dependency between the two classes.
- **Payoff:** operations on the data are gathered in one place, and code size drops.

## Object-Orientation Abusers

### Alternative Classes with Different Interfaces

- **Signs:** "Two classes perform identical functions but have different method names."
- **Causes:** the author of one class probably did not know that a functionally equivalent class already existed.
- **Treatment:** Rename Method to make the interfaces match; Move Method, Add Parameter, Parameterize Method; Extract Superclass if only part is duplicated. Afterwards one class may be deletable.
- **When to ignore:** "Sometimes merging classes is impossible or so difficult as to be pointless", for example classes in different libraries.
- **Payoff:** less duplicated code and a less bulky result.

### Refused Bequest

- **Signs:** a subclass uses only some of the methods and properties inherited from its parents, or redefines unneeded inherited methods to throw exceptions.
- **Causes:** inheritance created only to reuse code in a superclass, while "the superclass and subclass are completely different."
- **Treatment:** Replace Inheritance with Delegation when inheritance makes no sense; Extract Superclass when inheritance is appropriate, then remove the unneeded members from the subclass.
- **Payoff:** clarity and organisation. A `Dog` should not appear to inherit from a `Chair` just because both have four legs.

### Switch Statements

- **Signs:** "You have a complex `switch` operator or sequence of `if` statements."
- **Why it hurts:** "When a new condition is added, you have to find all the `switch` code and modify it."
- **Treatment:** "As a rule of thumb, when you see `switch` you should think of polymorphism." Extract Method, then Move Method; Replace Type Code with Subclasses or with State/Strategy; once the inheritance structure is in place, Replace Conditional with Polymorphism; Replace Parameter with Explicit Methods when a few conditions call the same method with different parameters; Introduce Null Object when one option is `null`.
- **When to ignore:** the `switch` performs simple actions, or it is used by Factory Method or Abstract Factory to choose which class to create.
- **Pitfall:** polymorphism can be superfluous when there are only a few conditions calling the same method with different parameters.
- **Payoff:** "Improved code organization."

### Temporary Field

- **Signs:** "Temporary fields get their values (and thus are needed by objects) only under certain circumstances." You expect data in the fields, but they are almost always empty.
- **Causes:** fields created so an algorithm needing many inputs does not need many parameters.
- **Treatment:** Extract Class, moving the fields and the code that uses them into a separate class (a method object, the same result as Replace Method with Method Object); Introduce Null Object to replace conditional checks for the field values.
- **Payoff:** "Better code clarity and organization."

## Change Preventers

"A change in one place forces many changes elsewhere, making development more complicated and expensive."

### Divergent Change

- **Signs:** "You find yourself having to change many unrelated methods when you make changes to a class." For example, adding a product type forces edits to the methods that find, display and order products. It is the opposite of Shotgun Surgery.
- **Causes:** poor program structure or "copypasta programming".
- **Treatment:** Extract Class; Extract Superclass and Extract Subclass when different classes share behaviour.
- **Payoff:** better organisation, less duplication, simpler support.

### Parallel Inheritance Hierarchies

- **Signs:** "Whenever you create a subclass for a class, you find yourself needing to create a subclass for another class." All is well while the hierarchy stays small.
- **Treatment:** make instances of one hierarchy refer to instances of the other, then remove the hierarchy in the referred class with Move Method and Move Field.
- **When to ignore:** "Sometimes having parallel class hierarchies is just a way to avoid even bigger mess with program architecture."
- **Pitfall:** de-duplication can produce even uglier code. If it does, revert and live with the current code.
- **Payoff:** less duplication and possibly better organisation.

### Shotgun Surgery

- **Signs:** "Making any modifications requires that you make many small changes to many different classes."
- **Causes:** "A single responsibility has been split up among a large number of classes." It can follow an overzealous application of the Divergent Change treatment.
- **Treatment:** Move Method and Move Field into a single class, creating one if none fits; Inline Class when the moved code leaves classes almost empty.
- **Payoff:** better organisation, less duplication, easier maintenance.

## Dispensables

### Comments

- **Signs:** "A method is filled with explanatory comments."
- **Why it hurts:** comments can be "a deodorant masking the smell of fishy code that could be improved." "The best comment is a good name for a method or class."
- **Treatment:** if code needs comments to be understood, change its structure so they are unnecessary: Extract Variable; Extract Method, using the comment text as a hint for the name; Rename Method; Introduce Assertion.
- **When to ignore:** comments that explain why something is implemented a certain way, and comments that explain a complex algorithm after other simplifications fell short.
- **Payoff:** more intuitive code.

### Duplicate Code

- **Signs:** "Two code fragments look almost identical." There is also subtler duplication, where parts of the code look different but perform the same job.
- **Causes:** developers do not know a colleague already wrote similar code.
- **Treatment:**
  - same code in one class: Extract Method;
  - same code in sibling subclasses: Extract Method, then Pull Up Field; in constructors, Pull Up Constructor Body;
  - similar but not identical code in sibling subclasses: Form Template Method;
  - two methods doing the same job with different algorithms: Substitute Algorithm;
  - same code in unrelated classes: Extract Superclass, or Extract Class and reference it;
  - many conditionals doing the same action: Consolidate Conditional Expression, then Extract Method;
  - identical code in every branch: Consolidate Duplicate Conditional Fragments.
- **When to ignore:** "In very rare cases, merging two identical fragments of code can make the code less intuitive and obvious."
- **Payoff:** "Merging duplicate code simplifies the structure of your code and makes it shorter."

### Data Class

- **Signs:** "a class that contains only fields and crude methods for accessing them (getters and setters)."
- **Why it hurts:** "the true power of objects is that they can contain behavior types or operations on their data."
- **Treatment:** Encapsulate Field; Encapsulate Collection; Move Method and Extract Method to move functionality from client code into the data class; Remove Setting Method and Hide Method.
- **When to ignore:** "It's a normal thing when a newly created class contains only a few public fields."
- **Payoff:** better understanding and organisation, and duplication in client code becomes visible.

### Dead Code

- **Signs:** "A variable, parameter, field, method or class is no longer used (usually because it's obsolete)." Also branches that have become unreachable.
- **Causes:** changed requirements or corrections, where "nobody had time to clean up the old code."
- **Treatment:** find it with a good IDE; delete unused code and files; Inline Class or Collapse Hierarchy for unnecessary classes; Remove Parameter for unneeded parameters.
- **Payoff:** "Reduced code size." "Simpler support."

### Lazy Class

- **Signs:** a class that "doesn't do enough to earn your attention".
- **Causes:** a class that became ridiculously small after refactoring, or one meant to support future development that never happened.
- **Treatment:** Inline Class for near-useless components; Collapse Hierarchy for subclasses with few functions.
- **When to ignore:** the class may be intentional, to signal future development. "Try to maintain a balance between clarity and simplicity in your code."
- **Payoff:** smaller code and easier maintenance.

### Speculative Generality

- **Signs:** "There's an unused class, method, field or parameter."
- **Why it hurts:** code written for anticipated features that never arrive is "hard to understand and support."
- **Treatment:** Collapse Hierarchy for an unused abstract class; Inline Class for unnecessary delegation; Inline Method for an unused method; Remove Parameter for unused parameters; delete unused fields.
- **When to ignore:** framework code may contain functionality the framework does not use itself if its users need it.
- **Pitfall:** before deleting an element, check whether unit tests use it.
- **Payoff:** slimmer code and easier support.

## Couplers

### Feature Envy

- **Signs:** "A method accesses the data of another object more than its own data."
- **Rule:** "if things change at the same time, you should keep them in the same place." Data and the functions that use it usually change together.
- **Treatment:** Move Method if the method clearly belongs elsewhere; Extract Method if only part of it uses the other object's data; for a method using several classes, place it in the class that holds most of the data.
- **When to ignore:** behaviour is sometimes kept separate from the data on purpose, as in Strategy and Visitor.
- **Payoff:** less duplication when data handling is centralised, and methods sit next to their data.

### Inappropriate Intimacy

- **Signs:** "One class uses the internal fields and methods of another class."
- **Rule:** "Good classes should know as little about each other as possible."
- **Treatment:** Move Method and Move Field, the simplest solution; Extract Class and Hide Delegate; Change Bidirectional Association to Unidirectional for mutual dependence; Replace Delegation with Inheritance for a subclass and superclass.
- **Pitfall:** moving members only works "if the first class truly doesn't need the moved parts."
- **Payoff:** better organisation, simpler support and reuse.

### Message Chains

- **Signs:** a series of calls such as `$a->b()->c()->d()`. A client requests an object, that object requests another, and so on.
- **Why it hurts:** "Any changes in these relationships require modifying the client."
- **Treatment:** Hide Delegate; or Extract Method, then Move Method, after asking why the end object is used at all.
- **Pitfall:** "Overly aggressive delegate hiding can cause code in which it's hard to see where the functionality is actually occurring", which leads to Middle Man.
- **Payoff:** fewer dependencies between the classes in the chain and less bloated code.

### Middle Man

- **Signs:** a class performs only one action, delegating work to another class.
- **Causes:** often an overzealous removal of Message Chains, leaving "an empty shell that doesn't do anything other than delegate."
- **Treatment:** "If most of a method's classes delegate to another class, Remove Middle Man is in order."
- **When to ignore:** a middle man created for a reason, such as avoiding interclass dependencies; Proxy and Decorator create middle men on purpose.
- **Payoff:** "Less bulky code."

## Other Smells

### Incomplete Library Class

- **Signs:** a library no longer meets your needs, and changing it is often impossible because it is read-only.
- **Treatment:** Introduce Foreign Method for a few added methods; Introduce Local Extension for big changes.
- **When to ignore:** extending a library can create extra work if changes to the library also require changes in your code.
- **Payoff:** "Reduces code duplication."

## Sources

- https://martinfowler.com/bliki/CodeSmell.html
- https://martinfowler.com/bliki/FunctionLength.html
- https://refactoring.guru/refactoring/smells
- https://refactoring.guru/smells/long-method
- https://refactoring.guru/smells/large-class
- https://refactoring.guru/smells/primitive-obsession
- https://refactoring.guru/smells/long-parameter-list
- https://refactoring.guru/smells/data-clumps
- https://refactoring.guru/smells/alternative-classes-with-different-interfaces
- https://refactoring.guru/smells/refused-bequest
- https://refactoring.guru/smells/switch-statements
- https://refactoring.guru/smells/temporary-field
- https://refactoring.guru/smells/divergent-change
- https://refactoring.guru/smells/parallel-inheritance-hierarchies
- https://refactoring.guru/smells/shotgun-surgery
- https://refactoring.guru/smells/comments
- https://refactoring.guru/smells/duplicate-code
- https://refactoring.guru/smells/data-class
- https://refactoring.guru/smells/dead-code
- https://refactoring.guru/smells/lazy-class
- https://refactoring.guru/smells/speculative-generality
- https://refactoring.guru/smells/feature-envy
- https://refactoring.guru/smells/inappropriate-intimacy
- https://refactoring.guru/smells/message-chains
- https://refactoring.guru/smells/middle-man
- https://refactoring.guru/smells/incomplete-library-class
