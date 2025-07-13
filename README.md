# RPG_project
🧙‍♂️ RPG Mini Project
This is a console-based RPG game written in Python. Players can create characters, form guilds, complete quests, craft items, engage in battles, and interact with factions, weather, and dynamic events.

🔥 Features
👤 Create characters with selectable classes: Warrior, Mage, or Rogue

⚔️ Turn-based combat with skills, effects, and damage types

🏰 Guild system with guild wars

🧪 Item crafting (rare and epic gear)

📜 Quest system with progression and rewards

🌤️ Dynamic weather system affecting stats

🧩 Faction diplomacy and reputation mechanics

🎲 Random events: dragon attacks, festivals, bandits, etc.

💾 Save/load full game state to JSON

🛒 Shop system with discounts and item tiers

🔄 Character-to-character trading

🗺️ Multiple battle locations with unique bonuses

🔮 Elemental combo system (e.g., fire + ice = stun effect)

🛠️ Installation
Make sure you have Python 3.7+ installed.

Clone or download the repository.

(Optional) Install any required packages:

bash
Kopiuj
Edytuj
pip install -r requirements.txt
⚠️ Currently, the project uses only Python's built-in modules. No external dependencies required.

🚀 How to Run
bash
Kopiuj
Edytuj
python mini_project(update).py
The game runs entirely through the terminal with text-based interaction.

🗂️ Project Structure
Game – the main class controlling menus, battles, events, and state

Character – holds character stats, inventory, actions, effects

Item, Effect, Enchantment, CraftingRecipe – full item and crafting system

Quest, Guild, Faction, GuildWar, DynamicEvent, WeatherSystem – RPG simulation mechanics

Game state is saved/loaded via game_save.json

🧠 Notes
The project is fully written in Ukrainian language (text, UI, class names).

Console interface only.

Designed with modular, extensible code – easy to add new features like enemies, items, locations, etc.

📄 License
This is an educational/learning project. You are free to use and modify it, crediting the original author.
