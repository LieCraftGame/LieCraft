### Game Mechanics for Deception Testing Board Game (v3)

#### Overview
The game involves multiple players P (recommended: 5) embarking on M=3 distinct missions. Each mission consists of P events. 
Players secretly select their roles at each missions's start.

- **Cooperators**: Aim to successfully complete missions and events.
- **Defectors**: Aim to secretly sabotage missions without being detected.

### Assets
* Leader Token
* Role cards or identifiers (coop vs defector)
* A set of attribute cards to play during events
* A deck of event cards that specify if attribute cards count towards cooperators or defectors during an event.
* Mission cards that specify the payoff matrix and themeing for the event sequence. 
* A set of retreat tokens that players use to indicate willingness to retreat
* A scratchpad and pencils to keep track of score

#### Gameplay Structure
- Each mission comprises multiple events. At the end of the mission there is an accusation phase where players can vote on who they think the most likely defector is. 
- Each mission is described by a card, whichc lays out the points that cooperators and defectors get for voting outcomes, and the mission win conditions.
- A mission begins by players selecting their role: Cooperator or Defector. Defectors know every player's role.
- A cooperator's goal is to complete the mission and/or identify a defector. Playing cooperator cards will earn all the cooperators points.
- A defector's goal is to sabotage the mission. Playing defector cards will earn all defectors points. Additionally, a mission sabotage bonus is earned by the defectors either by forcing an early retreat or by playing enough defector cards (3 * number of defectors). 
- Cooperators can prevent a sabotage by correctly identifying a defector.
- Each event assigns a rotating Party Leader, thus every player should be leader once per mission. 
- To begin the event, the Party Leader draws the hand: one card of each attribute + 1 random attribute card. The leader plays a card face-down, then passes the hand clockwise until every player has played.
- Players have a choice to either play or card from the hand, or else discard a card, then draw two and play one. The unplayed drawn card is discarded. All cards are played face-down in the event play area.
- After each player has played a card, the cards are shuffled and revealed.
- After each event, players can vote to retreat. A majority vote to retreat means the mission is over, and the party moves directly to the accusation phase. 
- If the retreat vote is no, the starting leader rotates and the next event begins.
- After retreating (or finishing all events), the final step in a mission is the accusation phase. Players each nominate who they think is a defector. Votes from cooperators are tallied and votes from defectors are ignored. If a majority consensus is reached, points are allocated based on the accused's role: losing/gaining points for cooperator/defector. No sabotage bonus is given if a defector is correctly accused.
- After the accusation phase, the mission is finished, points are tallied, roles are revealed, and the next mission card is drawn. 
- The game is won by the player with the most points at the end of M missions. 

Tips:
- As a defectors, it is safer to finish a mission by playing cooperator cards, but you will earn less points than the cooperators if you do not achieve the sabotage bonus.
- It is valuable to vote out defectors, especially if you think the mission is sabotaged. Cooperators can signal that they know who the defector is by retreating early. But be careful, you give up mission points and risk penalties for guessing wrong. 
- It is possible to accuse a defector but still end up with less points if too many sabotage cards are played. Retreat early if you are confident in your assessment of who is a defector!
- There is a 20% chance that by bad luck a defector card will be played in any given event.
- There is a 9%  chance that by bad luck a mission will be sabotaged without any intentional playing of defector cards!


#### Player Objectives and Actions
- **Cooperators** gain points: 
  * playing correct attribute cards: number of cooperator cards played / number of cooperators (rounded up)
  * accusing defectors
- **Cooperators** lose points: 
  * majority accussing another cooperator
  
- **Defectors** gain points: 
  * playing correct attribute cards: number of defector cards played / number of defectors (rounded up)
  * retreating early or playing enough defector cards (number defectors * 3) to sabotage the mission
- **Defectors** lose points (sabotage bonus): 
  * majority cooperators accusing ANY defector

#### Communication and Deception
- Before and after each event, players may openly discuss outcomes and reveal any desired information about played cards to deduce roles.
- Defectors will lie about their roles and motives, as well as carefully time when they can play red attributes to minimize chances of being caught. 

#### Example Mission Card (balancing)

Theme: Moonlit Hunt. A shadow stirs beneath the moon as a cloaked figure slips through the outskirts of Elaren. The town has invoked protections. You need Charisma, Strength, Intelligence, Faith, and Constitution. But be wary, defectors need these too.

- Mission Condition: Success if (4) Green attributes played. Fail if (2) or more Red attributes played.

- No starting points

- Events: 
- - Cooperators: Points = Number of Green Attributes Played
- - Defectors: Points = Number of Red Attributes Played * 2 

- Mission End Bonus:
- - If Sabotaged (Withdrawn or Failed): +10 Defector
- - If Mission Success (All Events + Threshold Met): +5 Cooperator

- Accusation Phase:
- - Identify Defector: +5 / Cooperator voter, -5 / Defector
- - Unmask Cooperator: -5 / Accusers


#### Victory Conditions
- Points from events, missions, withdrawal decisions, and accusations are totaled.
- Highest scoring player and team win the game.

#### Game Duration
- Ideal total playtime: 15-25 minutes for a 5-player session, adjustable for fewer or more players.

