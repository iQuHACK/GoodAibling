
_Organizer's note:_ this project won the **academia choice** award in iQuHACK 2020.

---

# Quantum Minesweeper!

Quantum Computing is mind-blowing, right? You know what else is bombastic and led user numbers to explode during the starting days of commercial classical computers? Yes, indeed, it's minesweeper! So let's push minesweeper into a new age of computing to blow up user number once more! 

We want to introduce to you the very first minesweeper game running on a quantum computer, or more precisely a quantum simulator at this point. The very nature of minesweeper is the exploration of a completely unkown playground and the indirect exploration of the fields to answer a simple binary question: Does a field contain a mine or not? A similar strategy is followed when reconstructing an unkown quantum state using quantum state tomography in a lab environment. The general principle behind quantum state tomography is that by repeatedly performing many different measurements on quantum systems, prepared in an identical way, frequency counts can be used to infer the underlying quantum state. Here, in this spirit, the mine field represents a pure, but possibly highly entangled, quantum state. Through repeated measurements, you will try to determine where the mines might be!


## How to play the game
The game board is composed by a 3 x 3 grid, which is represnted by a 9 qubit pure, but possibly highly entangled, quantum state. The game starts with 4 qubits that are deterministically set with 50% mines. Mines are represented by the computational basis state 1, while non mines are represented by state 0. The game is played in several rounds with two stages. 

### How a single round is played
The exploration stage comes first, where you learn about the underlying quantum state. Then, comes the scoring stage, where you attempt to not hit mines. Each round consists of 10 clicks, and each click performs a certain measurement several times as indicated on the screen. There are two types of measurements that can be performed.

1. A spin measurement in the computational basis (S_z). You activate this mode of measurement automatically, if you select **only one** square and hit enter. 
2. A parity measurement in the computational basis on several qubits. Here, we mean whether the number of 1s measured is even or odd. This mode is activated automatically, if you selected **more than one** square and hit enter.

The measurement is performed on several copies of the initial quantum state, and statistics are reported back. Use those statistics to chooe your next move wisely!

After you use up all 10 clicks, the game enters the scoring stage. Here, you need to use what you learned to try to avoid picking mines! You will be randomly given one of the two possible measurements above, and your goal is to measure a 0 with **single measurement(s)**. The scoring will work as follows:

1. If you are given a spin measurement, you can choose as many of the squares as you'd like, but you must choose at least one square. Then, spin measurements are performed one each qubit in sequential order. If you get a single 1 (mine) , you will lose, and the game is over. If you do not get any mines, your score is the number of boxes you selected and added to a running total.
2. If you are given a parity measurement, you can choose as many of the squares as you'd like, but you must choose at least two squares. Then, a parity measurement is done on all the qubits, and if you get 1 (odd number of mines), you will lose. If you get a 0, your score is the number of boxes you selected minus 1 and added to a running total.

### Multiple rounds
You will move on to the next round only if you did not lose the previous one! In subsequent rounds, the number of measurements for each click is reduced, while the number of clicks remain the same. Furthermore, the number of determinstically set bits reduces by 2 until there are no determinstically set bits in the 3rd round. The rules of each round remain the same, and there are a total of 5 rounds. Try to get the highest score possible, and have fun!

## What is quantum about the game?
When we first implemented this game, we had a 5 x 5 grid of mines (25 qubits), and used hundreds of gates to entangle them. When we gave it a go, our excitement quickly turned to dismay, as our program worked very slowly. It turned out that 25 qubits isn't so easy for a classical computer to simulate, and that is essentially what makes our game quantum. The initial game state itself is a quantum state! It simply could not work quickly on reasonable hardware, for instance, if we wanted a 10 x 10 highly entangled field. 

Then, we scaled down our grid to 3 x 3, where computational time on a simulator was no longer a barrier, but we quickly realized with a highly entangled field, the game was really hard! This makes sense, since our brains are pretty classical... However, we still wanted to make the game fun, so we decided to put in some deterministic qubits that you can "hunt" for, so to speak, and leave the rest entangled in a random way. 

Lastly, we wanted to encourage people to try to think quantum mechanically and have that affect their strategy, so we introduced the parity measurement. Classically, with independent bits, there is no reason to use this measurement in the information gathering stage. You might as well just try to discover single bit information about all the bits, and then assume roughly that the joint probability is the product of two single probabilities. In quantum mechanics, entangled states in general may not have this property. For instance, some 2 qubit bell states violate this dramatically. They have well defined parity, but very much not well defined single qubit measurements! We note that classically, one can just define a joint probability distribution with correlations, but this would require a lot of memory (exponential in the number of bits), and hence would need quantum computing capabilities anyway. We hope that you will thus use the parity measurement as you play this game. To further incentivize this, we randomized the required measurement in the scoring stage. 

Furthermore, there is one particular type of measurement that is inherently quantum, and requires quantum mechanical thinking. That is the multiple S_z measurement to get a higher score in the scoring stage. Each S_z measurement will collapse the state and thus affect subsequent S_z measurements. We regretably at the moment do not give the user the choice to specify the order of the measurements (it is simply sequential), but that can be in a future implementation. 

Quantum is here, and it starts with minesweeper!

## Details about the implementation
We use qiskit to handle the creation and measurement of the underlying quantum state. It is currently using the qiskit built-in quantum simulator, but can easily be modified to be used on real quantum hardware. The GUI is implemented in kivy. 
