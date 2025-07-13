import random
import json
import os
from enum import Enum
from typing import List, Dict, Optional
from collections import defaultdict


class ItemType(Enum):
    WEAPON = "Зброя"
    ARMOR = "Броня"
    POTION = "Зілля"
    ACCESSORY = "Аксесуар"


class ItemQuality(Enum):
    COMMON = "Звичайний"
    RARE = "Рідкісний"
    EPIC = "Епічний"
    LEGENDARY = "Легендарний"


class DamageType(Enum):
    PHYSICAL = "Фізична"
    FIRE = "Вогняна"
    ICE = "Крижана"
    POISON = "Отруйна"
    MAGICAL = "Магічна"


class EffectType(Enum):
    REGEN = "Регенерація"
    BURN = "Горіння"
    FREEZE = "Замороження"
    POISON = "Отрута"
    STUN = "Оглушення"


class CharacterClass(Enum):
    WARRIOR = "Воїн"
    MAGE = "Маг"
    ROGUE = "Розбійник"


class Effect:
    def __init__(self, effect_type: EffectType, duration: int, power: float):
        self.effect_type = effect_type
        self.duration = duration
        self.power = power

    def to_dict(self):
        return {
            "effect_type": self.effect_type.name,
            "duration": self.duration,
            "power": self.power
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            effect_type=EffectType[data["effect_type"]],
            duration=data["duration"],
            power=data["power"]
        )


class Enchantment:
    def __init__(self, name: str, effect_type: EffectType, power: float):
        self.name = name
        self.effect_type = effect_type
        self.power = power

    def to_dict(self):
        return {
            "name": self.name,
            "effect_type": self.effect_type.name,
            "power": self.power
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            effect_type=EffectType[data["effect_type"]],
            power=data["power"]
        )


class Item:
    def __init__(self, name: str, item_type: ItemType, power: float, value: int, quality: ItemQuality, item_set=None,
                 enchantment: Optional[Enchantment] = None, damage_type: Optional[DamageType] = None):
        self.name = name
        self.item_type = item_type
        self.power = power
        self.value = value
        self.quality = quality
        self.item_set = item_set
        self.enchantment = enchantment
        self.damage_type = damage_type

    def __str__(self):
        return f"{self.name} ({self.item_type.value}, {self.quality.value}, Сила: {self.power}, Вартість: {self.value})"

    def to_dict(self):
        return {
            "name": self.name,
            "item_type": self.item_type.name,
            "power": self.power,
            "value": self.value,
            "quality": self.quality.name,
            "item_set": self.item_set.name if self.item_set else None,
            "enchantment": self.enchantment.to_dict() if self.enchantment else None,
            "damage_type": self.damage_type.name if self.damage_type else None
        }

    @classmethod
    def from_dict(cls, data):
        item_set = None
        if data["item_set"]:
            item_set = type("ItemSet", (), {"name": data["item_set"]})()
        enchantment = Enchantment.from_dict(data["enchantment"]) if data["enchantment"] else None
        damage_type = DamageType[data["damage_type"]] if data["damage_type"] else None
        return cls(
            name=data["name"],
            item_type=ItemType[data["item_type"]],
            power=data["power"],
            value=data["value"],
            quality=ItemQuality[data["quality"]],
            item_set=item_set,
            enchantment=enchantment,
            damage_type=damage_type
        )


class Character:
    def __init__(self, nickname: str, char_class: CharacterClass):
        self.nickname = nickname
        self.char_class = char_class
        self.hp = 100
        self.max_hp = 100
        self.mana = 50
        self.max_mana = 50
        self.level = 1
        self.exp = 0
        self.gold = 100
        self.attack_power = 10
        self.defense = 5
        self.inventory: List[Item] = []
        self.equipped_items: Dict[ItemType, Item] = {}
        self.active_effects: List[Effect] = []
        self.skills = ["Сильний удар", "Захист"] if char_class == CharacterClass.WARRIOR else \
            ["Вогняна куля", "Магічний щит"] if char_class == CharacterClass.MAGE else \
                ["Постріл у спину", "Отруєне лезо"]
        self.skill_levels = {skill: 1 for skill in self.skills}
        self.reputation = {"Лицарі": 0, "Маги": 0, "Торговці": 0}
        self.active_quests = []

    def __str__(self):
        return f"{self.nickname} ({self.char_class.value}, Рівень {self.level}, HP: {self.hp}/{self.max_hp}, Мана: {self.mana}/{self.max_mana})"

    def calculate_damage(self):
        base_damage = self.attack_power
        for item in self.equipped_items.values():
            base_damage += item.power
        return base_damage

    def calculate_defense(self, damage_type: Optional[DamageType] = None):
        base_defense = self.defense
        for item in self.equipped_items.values():
            base_defense += item.power
        return base_defense

    def apply_effect(self, effect: Effect):
        self.active_effects.append(effect)
        print(f"{self.nickname} отримує ефект {effect.effect_type.value} на {effect.duration} раундів!")

    def update_effects(self):
        expired = []
        for effect in self.active_effects:
            effect.duration -= 1
            if effect.effect_type == EffectType.REGEN:
                self.hp = min(self.max_hp, self.hp + effect.power)
                print(f"{self.nickname} відновлює {effect.power} HP через {effect.effect_type.value}!")
            elif effect.effect_type == EffectType.BURN:
                self.hp -= effect.power
                print(f"{self.nickname} отримує {effect.power} шкоди від {effect.effect_type.value}!")
            elif effect.effect_type == EffectType.POISON:
                self.hp -= effect.power
                print(f"{self.nickname} отримує {effect.power} шкоди від {effect.effect_type.value}!")
            if effect.duration <= 0:
                expired.append(effect)
        self.active_effects = [e for e in self.active_effects if e not in expired]
        self.hp = max(0, self.hp)

    def add_exp(self, exp: int):
        self.exp += exp
        print(f"{self.nickname} отримує {exp} досвіду!")
        while self.exp >= self.level * 100:
            self.level += 1
            self.max_hp += 10
            self.hp = self.max_hp
            self.max_mana += 5
            self.mana = self.max_mana
            self.attack_power += 2
            self.defense += 1
            print(f"{self.nickname} досяг рівня {self.level}!")

    def equip_item(self, item: Item) -> bool:
        if item.item_type not in [ItemType.WEAPON, ItemType.ARMOR, ItemType.ACCESSORY]:
            print(f"Предмет {item.name} не можна екіпірувати!")
            return False
        self.equipped_items[item.item_type] = item
        print(f"{self.nickname} екіпірував {item.name}!")
        return True

    def use_item(self, item: Item) -> bool:
        if item.item_type != ItemType.POTION:
            print(f"Предмет {item.name} не є зіллям!")
            return False
        self.hp = min(self.max_hp, self.hp + item.power)
        self.inventory.remove(item)
        print(f"{self.nickname} використав {item.name} і відновив {item.power} HP!")
        return True

    def attack(self, target: 'Character') -> bool:
        if any(e.effect_type == EffectType.STUN for e in self.active_effects):
            print(f"{self.nickname} оглушений і пропускає хід!")
            return False
        if any(e.effect_type == EffectType.FREEZE for e in self.active_effects):
            print(f"{self.nickname} заморожений і пропускає хід!")
            return False
        damage = self.calculate_damage()
        defense = target.calculate_defense()
        actual_damage = max(1, damage - defense * 0.5)
        target.hp -= actual_damage
        print(f"{self.nickname} атакує {target.nickname} і завдає {actual_damage:.1f} шкоди!")
        return True

    def use_skill(self, skill_name: str, targets: List['Character'], game: 'Game') -> bool:
        skill_effects = {
            "Сильний удар": lambda: ("завдає потужного удару", None, 1.5 * self.skill_levels.get("Сильний удар", 1),
                                     DamageType.PHYSICAL),
            "Захист": lambda: ("піднімає щит", Effect(EffectType.REGEN, 3, 5 * self.skill_levels.get("Захист", 1)), 0,
                               None),
            "Розгром": lambda: ("розмахує зброєю по всіх ворогах", None, 1.2 * self.skill_levels.get("Розгром", 1),
                                DamageType.PHYSICAL),
            "Вогняна куля": lambda: ("кидає вогняну кулю",
                                     Effect(EffectType.BURN, 2, 3 * self.skill_levels.get("Вогняна куля", 1)),
                                     1.2 * self.skill_levels.get("Вогняна куля", 1), DamageType.FIRE),
            "Морозний поцілунок": lambda: ("заморожує ворога", Effect(EffectType.FREEZE, 1, 0),
                                           0.8 * self.skill_levels.get("Морозний поцілунок", 1), DamageType.ICE),
            "Магічний щит": lambda: ("створює магічний бар'єр",
                                     Effect(EffectType.REGEN, 2, 3 * self.skill_levels.get("Магічний щит", 1)), 0,
                                     None),
            "Лікування": lambda: ("лікує союзників",
                                  Effect(EffectType.REGEN, 2, 10 * self.skill_levels.get("Лікування", 1)), 0, None),
            "Божественний щит": lambda: ("створює захисний бар'єр", None, 0, None),
            "Очищення": lambda: ("знімає негативні ефекти", None, 0, None),
            "Стіна щитів": lambda: ("блокує атаки", None, 0, None),
            "Протиудар": lambda: ("контратакує", None, 1.3 * self.skill_levels.get("Протиудар", 1),
                                  DamageType.PHYSICAL),
            "Землетрус": lambda: ("викликає землетрус", Effect(EffectType.STUN, 1, 0),
                                  1.0 * self.skill_levels.get("Землетрус", 1), DamageType.PHYSICAL),
            "Постріл у спину": lambda: ("атакує з прихованої позиції", None,
                                        1.8 * self.skill_levels.get("Постріл у спину", 1), DamageType.PHYSICAL),
            "Отруєне лезо": lambda: ("отруює ворога",
                                     Effect(EffectType.POISON, 3, 4 * self.skill_levels.get("Отруєне лезо", 1)), 1.0,
                                     DamageType.POISON),
            "Тіньовий удар": lambda: ("атакує з тіні", None, 1.5 * self.skill_levels.get("Тіньовий удар", 1),
                                      DamageType.MAGICAL)
        }

        if skill_name not in self.skills:
            print(f"{self.nickname} не знає навички {skill_name}!")
            return False

        description, effect, multiplier, damage_type = skill_effects[skill_name]()
        print(f"{self.nickname} {description}!")

        used_elements = [damage_type] if damage_type else []
        for target in targets:
            if multiplier > 0:
                damage = self.calculate_damage() * multiplier
                defense = target.calculate_defense(damage_type) if damage_type else 0
                actual_damage = max(1, damage - defense * 0.5)
                target.hp -= actual_damage
                print(
                    f"Завдано {actual_damage:.1f} {damage_type.value if damage_type else ''} шкоди {target.nickname}!")
            if effect:
                target.apply_effect(effect)

        if used_elements:
            game.apply_elemental_combo(self, targets, used_elements)

        return True

    def to_dict(self):
        return {
            "nickname": self.nickname,
            "char_class": self.char_class.name,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "mana": self.mana,
            "max_mana": self.max_mana,
            "level": self.level,
            "exp": self.exp,
            "gold": self.gold,
            "attack_power": self.attack_power,
            "defense": self.defense,
            "inventory": [item.to_dict() for item in self.inventory],
            "equipped_items": {k.name: v.to_dict() for k, v in self.equipped_items.items()},
            "active_effects": [effect.to_dict() for effect in self.active_effects],
            "skills": self.skills,
            "skill_levels": self.skill_levels,
            "reputation": self.reputation,
            "active_quests": [quest.id for quest in self.active_quests]
        }

    @classmethod
    def from_dict(cls, data):
        character = cls(data["nickname"], CharacterClass[data["char_class"]])
        character.hp = data["hp"]
        character.max_hp = data["max_hp"]
        character.mana = data["mana"]
        character.max_mana = data["max_mana"]
        character.level = data["level"]
        character.exp = data["exp"]
        character.gold = data["gold"]
        character.attack_power = data["attack_power"]
        character.defense = data["defense"]
        character.inventory = [Item.from_dict(item) for item in data["inventory"]]
        character.equipped_items = {ItemType[k]: Item.from_dict(v) for k, v in data["equipped_items"].items()}
        character.active_effects = [Effect.from_dict(effect) for effect in data["active_effects"]]
        character.skills = data["skills"]
        character.skill_levels = data["skill_levels"]
        character.reputation = data["reputation"]
        # active_quests will be restored after loading quests
        return character


class Quest:
    def __init__(self, id: str, title: str, description: str, objectives: Dict[str, int], rewards: Dict):
        self.id = id
        self.title = title
        self.description = description
        self.objectives = objectives
        self.rewards = rewards
        self.progress = {obj: 0 for obj in objectives}

    def update_progress(self, objective: str, amount: int = 1):
        if objective in self.progress:
            self.progress[objective] += amount
            print(f"Прогрес квесту '{self.title}': {objective} {self.progress[objective]}/{self.objectives[objective]}")

    def is_completed(self) -> bool:
        return all(self.progress[obj] >= goal for obj, goal in self.objectives.items())

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "objectives": self.objectives,
            "rewards": {
                "gold": self.rewards.get("gold", 0),
                "exp": self.rewards.get("exp", 0),
                "item": self.rewards["item"].to_dict() if "item" in self.rewards else None
            },
            "progress": self.progress
        }

    @classmethod
    def from_dict(cls, data):
        rewards = {
            "gold": data["rewards"]["gold"],
            "exp": data["rewards"]["exp"]
        }
        if data["rewards"]["item"]:
            rewards["item"] = Item.from_dict(data["rewards"]["item"])
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            objectives=data["objectives"],
            rewards=rewards
        )


class WeatherType(Enum):
    CLEAR = "Ясно"
    RAIN = "Дощ"
    STORM = "Гроза"
    FOG = "Туман"


class WeatherSystem:
    def __init__(self):
        self.current_weather = WeatherType.CLEAR
        self.weather_effects = {
            WeatherType.CLEAR: {"attack_power": 0.0, "defense": 0.0},
            WeatherType.RAIN: {"attack_power": -0.1, "defense": 0.0},
            WeatherType.STORM: {"attack_power": -0.2, "mana_cost_multiplier": 0.1},
            WeatherType.FOG: {"attack_power": -0.15, "defense": -0.1}
        }

    def update_weather(self, location):
        self.current_weather = random.choice(list(WeatherType))
        print(f"Погода в локації {location.name}: {self.current_weather.value}")

    def get_weather_effects(self):
        return self.weather_effects[self.current_weather]

    def to_dict(self):
        return {"current_weather": self.current_weather.name}

    def from_dict(self, data):
        self.current_weather = WeatherType[data["current_weather"]]


class Location:
    def __init__(self, name: str, battle_modifiers: Dict[str, float], description: str):
        self.name = name
        self.battle_modifiers = battle_modifiers
        self.description = description

    def to_dict(self):
        return {
            "name": self.name,
            "battle_modifiers": self.battle_modifiers,
            "description": self.description
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            battle_modifiers=data["battle_modifiers"],
            description=data["description"]
        )


class Guild:
    def __init__(self, name: str, members: List[Character] = None):
        self.name = name
        self.members = members or []
        self.reputation = 0

    def add_member(self, character: Character):
        if character not in self.members:
            self.members.append(character)
            print(f"{character.nickname} приєднався до гільдії {self.name}!")
            character.reputation[self.name] = character.reputation.get(self.name, 0) + 10

    def remove_member(self, character: Character):
        if character in self.members:
            self.members.remove(character)
            print(f"{character.nickname} покинув гільдію {self.name}!")
            character.reputation[self.name] = character.reputation.get(self.name, 0) - 10

    def to_dict(self):
        return {
            "name": self.name,
            "members": [char.nickname for char in self.members],
            "reputation": self.reputation
        }

    @classmethod
    def from_dict(cls, data):
        return cls(name=data["name"], members=[])


class Faction:
    def __init__(self, name: str, relations: Dict[str, float], bonuses: Dict[str, float]):
        self.name = name
        self.relations = relations
        self.bonuses = bonuses

    def update_relations(self, faction_name: str, amount: float):
        self.relations[faction_name] = max(0.0, min(1.0, self.relations.get(faction_name, 0.5) + amount))
        print(f"Відносини з {faction_name} змінено: {self.relations[faction_name]:.2f}")

    def to_dict(self):
        return {
            "name": self.name,
            "relations": self.relations,
            "bonuses": self.bonuses
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            relations=data["relations"],
            bonuses=data["bonuses"]
        )


class GuildWar:
    def __init__(self, guild1: Guild, guild2: Guild, stakes: Dict[str, float]):
        self.guild1 = guild1
        self.guild2 = guild2
        self.stakes = stakes
        self.winner = None

    def resolve_war(self, game: 'Game') -> Optional[Guild]:
        print(f"\n⚔️ Гільдійська війна: {self.guild1.name} проти {self.guild2.name}!")
        guild1_power = sum(getattr(c, "attack_power", 0) + getattr(c, "defense", 0) for c in self.guild1.members)
        guild2_power = sum(getattr(c, "attack_power", 0) + getattr(c, "defense", 0) for c in self.guild2.members)

        if guild1_power > guild2_power * (1 + 0.1 * game.difficulty):
            self.winner = self.guild1
            print(f"Гільдія {self.guild1.name} перемогла!")
        elif guild2_power > guild1_power * (1 + 0.1 * game.difficulty):
            self.winner = self.guild2
            print(f"Гільдія {self.guild2.name} перемогла!")
        else:
            print("Нічия у війні!")
            return None

        for char in self.winner.members:
            char.gold += self.stakes.get("gold", 0)
            char.add_exp(self.stakes.get("exp", 0))
            char.reputation["Лицарі"] += self.stakes.get("reputation", 0)
            print(
                f"{char.nickname} отримав {self.stakes.get('gold', 0)} золота, {self.stakes.get('exp', 0)} досвіду та +{self.stakes.get('reputation', 0)} репутації!")

        return self.winner

    def to_dict(self):
        return {
            "guild1": self.guild1.name,
            "guild2": self.guild2.name,
            "stakes": self.stakes,
            "winner": self.winner.name if self.winner else None
        }

    @classmethod
    def from_dict(cls, data, guilds: List[Guild]):
        guild1 = next(g for g in guilds if g.name == data["guild1"])
        guild2 = next(g for g in guilds if g.name == data["guild2"])
        war = cls(guild1, guild2, data["stakes"])
        war.winner = next((g for g in guilds if g.name == data["winner"]), None)
        return war


class ElementalEffect:
    def __init__(self, name: str, elements: List[DamageType], effect: Effect):
        self.name = name
        self.elements = elements
        self.effect = effect

    def to_dict(self):
        return {
            "name": self.name,
            "elements": [e.name for e in self.elements],
            "effect": self.effect.to_dict()
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            elements=[DamageType[e] for e in data["elements"]],
            effect=Effect.from_dict(data["effect"])
        )


class DynamicEvent:
    def __init__(self, name: str, description: str, condition: callable, effect: callable, location: str = None):
        self.name = name
        self.description = description
        self.condition = condition
        self.effect = effect
        self.location = location

    def can_trigger(self, game: 'Game') -> bool:
        return (not self.location or game.current_location.name == self.location) and self.condition(game)

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "location": self.location
        }

    @classmethod
    def from_dict(cls, data):
        conditions = {
            "Напад дракона": lambda g: g.day >= 5,
            "Свято врожаю": lambda g: g.day % 7 == 0,
            "Магічний шторм": lambda g: g.weather_system.current_weather == WeatherType.STORM
        }
        effects = {
            "Напад дракона": lambda g: [c.apply_effect(Effect(EffectType.BURN, 3, 10)) for c in g.characters],
            "Свято врожаю": lambda g: [c.add_exp(100) or setattr(c, 'gold', c.gold + 200) for c in g.characters],
            "Магічний шторм": lambda g: [c.apply_effect(Effect(EffectType.STUN, 1, 0)) for c in g.characters if
                                         c.char_class == CharacterClass.MAGE]
        }
        return cls(
            name=data["name"],
            description=data["description"],
            condition=conditions[data["name"]],
            effect=effects[data["name"]],
            location=data["location"]
        )


class CraftingRecipe:
    def __init__(self, name: str, required_items: Dict[str, int], result: Item):
        self.name = name
        self.required_items = required_items
        self.result = result

    def can_craft(self, inventory: List[Item]) -> bool:
        item_counts = defaultdict(int)
        for item in inventory:
            item_counts[item.name] += 1
        return all(item_counts.get(item, 0) >= count for item, count in self.required_items.items())

    def craft(self, character: Character):
        for item_name, count in self.required_items.items():
            for _ in range(count):
                for item in character.inventory[:]:
                    if item.name == item_name:
                        character.inventory.remove(item)
                        break
        character.inventory.append(self.result)
        print(f"{character.nickname} створив {self.result.name}!")

    def to_dict(self):
        return {
            "name": self.name,
            "required_items": self.required_items,
            "result": self.result.to_dict()
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            required_items=data["required_items"],
            result=Item.from_dict(data["result"])
        )


class Game:
    def __init__(self):
        self.characters: List[Character] = []
        self.teams: Dict[str, List[Character]] = {}
        self.quests: List[Quest] = []
        self.weather_system = WeatherSystem()
        self.current_round = 1
        self.day = 1
        self.difficulty = 1
        self.current_location = None
        self.guilds: List[Guild] = []
        self.factions: List[Faction] = []
        self.guild_wars: List[GuildWar] = []
        self.elemental_effects: List[ElementalEffect] = []
        self.dynamic_events: List[DynamicEvent] = []
        self.crafting_recipes: List[CraftingRecipe] = []
        self.warrior_set = type("ItemSet", (), {"name": "Набір воїна"})()
        self.mage_set = type("ItemSet", (), {"name": "Набір мага"})()
        self.events = [
            type("Event", (), {
                "name": "Зустріч із мудрецем",
                "description": "Мудрець ділиться знаннями, підвищуючи досвід.",
                "effect": lambda g: [c.add_exp(50) for c in g.characters]
            })(),
            type("Event", (), {
                "name": "Грабіжники",
                "description": "Банда грабіжників атакує, зменшуючи золото.",
                "effect": lambda g: [setattr(c, 'gold', max(0, c.gold - 20)) for c in g.characters]
            })()
        ]
        self._init_quests()
        self._init_item_sets()
        self._init_locations()
        self._init_guilds()
        self._init_factions()
        self._init_elemental_effects()
        self._init_dynamic_events()
        self._init_crafting_recipes()

    def _init_quests(self):
        self.quests.append(Quest(
            "first_blood",
            "Перша кров",
            "Перемогти 5 ворогів",
            {"enemies_defeated": 5},
            {"gold": 100, "exp": 50}
        ))
        self.quests.append(Quest(
            "item_collector",
            "Колекціонер",
            "Зібрати 3 рідкісних предмети",
            {"rare_items": 3},
            {"gold": 200, "exp": 100}
        ))
        self.quests.append(Quest(
            "boss_hunter",
            "Мисливець на боса",
            "Перемогти могутнього боса",
            {"boss_defeated": 1},
            {"gold": 500, "exp": 200, "item": Item("Меч дракона", ItemType.WEAPON, 20, 300, ItemQuality.LEGENDARY)}
        ))
        self.quests.append(Quest(
            "guild_honor",
            "Честь гільдії",
            "Виграти бій з усіма членами однієї гільдії",
            {"guild_victory": 1},
            {"gold": 300, "exp": 150}
        ))
        self.quests.append(Quest(
            "faction_alliance",
            "Союз із фракцією",
            "Досягти максимальних відносин із фракцією",
            {"max_relations": 1},
            {"gold": 400, "exp": 200, "item": Item("Амулет дипломата", ItemType.ACCESSORY, 10, 150, ItemQuality.EPIC)}
        ))

    def _init_item_sets(self):
        pass  # Already defined as simple objects in __init__

    def _init_locations(self):
        self.locations = [
            Location("Ліс", {"attack_power": 0.1, "defense": 0.0}, "Густий ліс із небезпечними істотами."),
            Location("Гори", {"defense": 0.2, "attack_power": -0.1}, "Суворий гірський ландшафт."),
            Location("Пустеля", {"attack_power": 0.15, "mana_cost_multiplier": 0.1},
                     "Спекотна пустеля з піщаними бурями.")
        ]
        self.current_location = self.locations[0]

    def _init_guilds(self):
        self.guilds = [
            Guild("Лицарі світла"),
            Guild("Тіні ночі"),
            Guild("Магічний орден")
        ]

    def _init_factions(self):
        self.factions = [
            Faction(
                "Лицарі",
                {"Маги": 0.5, "Торговці": 0.7},
                {"discount": 0.1, "attack_power": 0.05}
            ),
            Faction(
                "Маги",
                {"Лицарі": 0.5, "Торговці": 0.6},
                {"magic_power": 0.1, "mana_cost_multiplier": -0.1}
            ),
            Faction(
                "Торговці",
                {"Лицарі": 0.7, "Маги": 0.6},
                {"discount": 0.2, "gold_bonus": 0.1}
            )
        ]

    def _init_elemental_effects(self):
        self.elemental_effects = [
            ElementalEffect(
                "Пара",
                [DamageType.FIRE, DamageType.ICE],
                Effect(EffectType.STUN, 2, 0)
            ),
            ElementalEffect(
                "Вибух",
                [DamageType.FIRE, DamageType.PHYSICAL],
                Effect(EffectType.BURN, 3, 5)
            ),
            ElementalEffect(
                "Отруйна хмара",
                [DamageType.POISON, DamageType.MAGICAL],
                Effect(EffectType.POISON, 3, 7)
            )
        ]

    def _init_dynamic_events(self):
        self.dynamic_events = [
            DynamicEvent(
                "Напад дракона",
                "Дракон атакує вашу команду!",
                lambda game: game.day >= 5,
                lambda game: [c.apply_effect(Effect(EffectType.BURN, 3, 10)) for c in game.characters],
                "Гори"
            ),
            DynamicEvent(
                "Свято врожаю",
                "Ви берете участь у святі, отримуючи бонуси!",
                lambda game: game.day % 7 == 0,
                lambda game: [c.add_exp(100) or setattr(c, 'gold', c.gold + 200) for c in game.characters],
                "Ліс"
            ),
            DynamicEvent(
                "Магічний шторм",
                "Гроза викликає магічні перешкоди!",
                lambda game: game.weather_system.current_weather == WeatherType.STORM,
                lambda game: [c.apply_effect(Effect(EffectType.STUN, 1, 0)) for c in game.characters if
                              c.char_class == CharacterClass.MAGE],
                "Пустеля"
            )
        ]

    def _init_crafting_recipes(self):
        self.crafting_recipes = [
            CraftingRecipe(
                "Вогняний меч",
                {"Шкіряна броня": 1, "Меч лицаря": 1},
                Item("Вогняний меч", ItemType.WEAPON, 15, 200, ItemQuality.EPIC, damage_type=DamageType.FIRE)
            ),
            CraftingRecipe(
                "Крижаний щит",
                {"Щит воїна": 1, "Зілля здоров'я": 2},
                Item("Крижаний щит", ItemType.ARMOR, 12, 180, ItemQuality.EPIC, damage_type=DamageType.ICE)
            )
        ]

    def create_character(self):
        try:
            nickname = input("Введіть ім'я персонажа: ")
            if not nickname.strip():
                print("Ім'я не може бути порожнім!")
                return
            print("\nВиберіть клас персонажа:")
            for i, char_class in enumerate(CharacterClass, 1):
                print(f"{i}. {char_class.value}")
            class_choice = int(input("Виберіть клас (1-3): ")) - 1
            if class_choice not in range(len(CharacterClass)):
                print("Некоректний вибір!")
                return
            char_class = list(CharacterClass)[class_choice]
            character = Character(nickname, char_class)
            self.characters.append(character)
            print(f"Персонаж {nickname} ({char_class.value}) створений!")
        except (ValueError, EOFError):
            print("Помилка введення. Створення персонажа скасовано.")

    def show_character_status(self, character: Character):
        print(f"\nСтатус персонажа {character.nickname}:")
        print(f"Клас: {character.char_class.value}")
        print(f"Рівень: {character.level}")
        print(f"HP: {character.hp}/{character.max_hp}")
        print(f"Мана: {character.mana}/{character.max_mana}")
        print(f"Досвід: {character.exp}/{character.level * 100}")
        print(f"Золото: {character.gold}")
        print(f"Сила атаки: {character.attack_power}")
        print(f"Захист: {character.defense}")
        print("Екіпіровані предмети:")
        for item_type, item in character.equipped_items.items():
            print(f"  {item_type.value}: {item}")
        print("Інвентар:")
        for item in character.inventory:
            print(f"  {item}")
        print("Активні ефекти:")
        for effect in character.active_effects:
            print(f"  {effect.effect_type.value} (Тривалість: {effect.duration}, Сила: {effect.power})")
        print("Навички:")
        for skill in character.skills:
            print(f"  {skill} (Рівень {character.skill_levels[skill]})")
        print("Репутація:")
        for faction, value in character.reputation.items():
            print(f"  {faction}: {value}")

    def shop(self, character: Character):
        print("\n🏪 Магазин:")
        discount = 0.1 if character.reputation["Торговці"] >= 50 else 0.0
        for faction in self.factions:
            if faction.name == "Торговці" and faction.relations.get("Лицарі", 0.5) >= 0.8:
                discount += faction.bonuses.get("discount", 0.0)
        print(f"Ваше золото: {character.gold} (Знижка: {discount * 100:.0f}%)")
        items = [self.generate_loot(self.difficulty) for _ in range(3)]
        print("Доступні товари:")
        for i, item in enumerate(items, 1):
            price = int(item.value * (1 - discount))
            print(f"{i}. {item} (Ціна: {price})")
        try:
            choice = int(input("Виберіть предмет для покупки (0 для скасування): ")) - 1
            if choice == -1:
                return
            if not (0 <= choice < len(items)):
                print("Некоректний вибір!")
                return
            item = items[choice]
            price = int(item.value * (1 - discount))
            if character.gold >= price:
                character.gold -= price
                character.inventory.append(item)
                print(f"{character.nickname} купив {item.name} за {price} золота!")
                if item.quality in [ItemQuality.RARE, ItemQuality.EPIC, ItemQuality.LEGENDARY]:
                    for quest in character.active_quests:
                        if "rare_items" in quest.objectives:
                            quest.update_progress("rare_items")
            else:
                print("Недостатньо золота!")
        except (ValueError, EOFError):
            print("Помилка введення. Покупка скасована.")

    def generate_loot(self, difficulty: int = 1) -> Item:
        quality_roll = random.random()
        if quality_roll > 0.95 - 0.05 * self.difficulty:
            quality = ItemQuality.LEGENDARY
        elif quality_roll > 0.8 - 0.05 * self.difficulty:
            quality = ItemQuality.EPIC
        elif quality_roll > 0.5 - 0.05 * self.difficulty:
            quality = ItemQuality.RARE
        else:
            quality = ItemQuality.COMMON

        item_type = random.choice(list(ItemType))
        base_power = random.randint(5, 15) * self.difficulty
        value = base_power * 10

        enchantment = None
        if random.random() > 0.7:
            enchant_types = [EffectType.BURN, EffectType.FREEZE, EffectType.POISON]
            enchantment = Enchantment(
                name="Чари " + random.choice(["вогню", "льоду", "отрути"]),
                effect_type=random.choice(enchant_types),
                power=random.uniform(0.1, 0.3)
            )

        item_set = None
        if random.random() > 0.9:
            item_set = random.choice([self.warrior_set, self.mage_set])

        damage_type = random.choice(
            [DamageType.PHYSICAL, DamageType.FIRE, DamageType.ICE, DamageType.POISON, DamageType.MAGICAL])

        prefixes = {
            DamageType.FIRE: "Вогняний",
            DamageType.ICE: "Крижаний",
            DamageType.POISON: "Отруйний",
            DamageType.MAGICAL: "Магічний",
            DamageType.PHYSICAL: ""
        }

        name = prefixes.get(damage_type, "") + " " + item_type.value.lower()
        name = name.strip()

        return Item(
            name=name,
            item_type=item_type,
            power=base_power,
            value=value,
            quality=quality,
            item_set=item_set,
            enchantment=enchantment,
            damage_type=damage_type
        )

    def team_selection(self):
        self.teams = {}
        print("\nФормування команд:")
        available_chars = self.characters.copy()
        team_id = 1
        while available_chars:
            print(f"\nФормування команди {team_id}:")
            print("Доступні персонажі:")
            for i, char in enumerate(available_chars, 1):
                print(f"{i}. {char.nickname} ({char.char_class.value})")
            print("0. Завершити формування команди")
            try:
                choice = int(input("Виберіть персонажа (0 для завершення): ")) - 1
                if choice == -1:
                    if f"Команда {team_id}" in self.teams and self.teams[f"Команда {team_id}"]:
                        team_id += 1
                    else:
                        print("Команда не може бути порожньою!")
                    if not available_chars:
                        break
                    continue
                if 0 <= choice < len(available_chars):
                    if f"Команда {team_id}" not in self.teams:
                        self.teams[f"Команда {team_id}"] = []
                    self.teams[f"Команда {team_id}"].append(available_chars.pop(choice))
                    print(f"{self.teams[f'Команда {team_id}'][-1].nickname} додано до Команди {team_id}")
                else:
                    print("Некоректний вибір!")
            except (ValueError, EOFError):
                print("Помилка введення. Пропуск.")

    def apply_weather_effects(self):
        effects = self.weather_system.get_weather_effects()
        for character in self.characters:
            for stat, value in effects.items():
                current_value = getattr(character, stat, 0)
                setattr(character, stat, current_value * (1 + value))
            print(f"Погода впливає на {character.nickname}: {self.weather_system.current_weather.value}")

    def player_turn(self, character: Character, enemies: List[Character]):
        print(f"\nХід гравця {character.nickname}")
        print("1. Атакувати")
        print("2. Використати навичку")
        print("3. Використати предмет")
        print("4. Показати статус")
        print("5. Пропустити хід")

        while True:
            try:
                choice = int(input("Виберіть дію: "))
                if choice == 1:
                    print("\nВибір цілі:")
                    for i, enemy in enumerate(enemies, 1):
                        print(f"{i}. {enemy.nickname} ({enemy.hp:.1f} HP)")
                    target_choice = int(input("Виберіть ціль: ")) - 1
                    if 0 <= target_choice < len(enemies):
                        return character.attack(enemies[target_choice])
                    print("Некоректний номер!")
                elif choice == 2:
                    if not character.skills:
                        print("Немає доступних навичок!")
                        continue
                    print("\nДоступні навички:")
                    for i, skill in enumerate(character.skills, 1):
                        print(f"{i}. {skill} (Рівень {character.skill_levels[skill]})")
                    skill_choice = int(input("Виберіть навичку: ")) - 1
                    if 0 <= skill_choice < len(character.skills):
                        print("\nВибір цілей:")
                        for i, enemy in enumerate(enemies, 1):
                            print(f"{i}. {enemy.nickname} ({enemy.hp:.1f} HP)")
                        targets_input = input("Виберіть цілі (через кому): ").split(',')
                        targets = []
                        for num in targets_input:
                            idx = int(num.strip()) - 1
                            if 0 <= idx < len(enemies):
                                targets.append(enemies[idx])
                        if targets:
                            return character.use_skill(character.skills[skill_choice], targets, self)
                        print("Некоректні цілі!")
                    print("Некоректний номер!")
                elif choice == 3:
                    if not character.inventory:
                        print("Інвентар порожній!")
                        continue
                    print("\nІнвентар:")
                    for i, item in enumerate(character.inventory, 1):
                        print(f"{i}. {item}")
                    item_choice = int(input("Виберіть предмет: ")) - 1
                    if 0 <= item_choice < len(character.inventory):
                        item = character.inventory[item_choice]
                        if item.item_type == ItemType.POTION:
                            return character.use_item(item)
                        else:
                            if character.equip_item(item):
                                return False
                    print("Некоректний номер!")
                elif choice == 4:
                    self.show_character_status(character)
                elif choice == 5:
                    print(f"{character.nickname} пропускає хід.")
                    return False
                else:
                    print("Некоректний вибір!")
            except (ValueError, EOFError):
                print("Помилка введення. Пропуск ходу.")
                return False

    def enemy_turn(self, enemy: Character, targets: List[Character]):
        if any(e.effect_type == EffectType.STUN for e in enemy.active_effects):
            print(f"{enemy.nickname} оглушений і пропускає хід!")
            return
        if any(e.effect_type == EffectType.FREEZE for e in enemy.active_effects):
            print(f"{enemy.nickname} заморожений і пропускає хід!")
            return
        target = random.choice(targets)
        if random.random() < 0.5 and enemy.skills:
            skill = random.choice(enemy.skills)
            enemy.use_skill(skill, [target], self)
        else:
            enemy.attack(target)

    def battle(self):
        print(f"\n⚔️ Початок битви в локації {self.current_location.name}!")
        self.weather_system.update_weather(self.current_location)
        self.apply_weather_effects()

        for character in self.characters:
            for stat, value in self.current_location.battle_modifiers.items():
                current_value = getattr(character, stat, 0)
                setattr(character, stat, current_value * (1 + value))
            for faction in self.factions:
                if character.reputation[faction.name] >= 50 and faction.relations.get("Лицарі", 0.5) >= 0.8:
                    for stat, value in faction.bonuses.items():
                        if stat != "discount":
                            current_value = getattr(character, stat, 0)
                            setattr(character, stat, current_value * (1 + value))

        self.current_round = 1
        teams = list(self.teams.values())
        team1, team2 = teams[0], teams[1]
        while team1 and team2:
            print(f"\nРаунд {self.current_round}")
            for character in team1:
                if character.hp > 0:
                    self.player_turn(character, team2)
                    for c in team2[:]:
                        if c.hp <= 0:
                            team2.remove(c)
                            print(f"{c.nickname} переможений!")
                            for quest in character.active_quests:
                                if "enemies_defeated" in quest.objectives:
                                    quest.update_progress("enemies_defeated")
            for enemy in team2:
                if enemy.hp > 0:
                    self.enemy_turn(enemy, team1)
                    for c in team1[:]:
                        if c.hp <= 0:
                            team1.remove(c)
                            print(f"{c.nickname} переможений!")
            for character in team1 + team2:
                character.update_effects()
            self.current_round += 1
            if not team1 or not team2:
                break

        winner = team1 if team1 else team2
        print(f"\nБитва завершена! Переможець: {'Команда 1' if team1 else 'Команда 2'}")
        for char in winner:
            loot = self.generate_loot(self.difficulty)
            char.inventory.append(loot)
            char.add_exp(50 * self.difficulty)
            char.gold += 100 * self.difficulty
            char.reputation["Лицарі"] += 5
            print(f"{char.nickname} отримує {loot}, 50 досвіду і 100 золота!")
            for guild in self.guilds:
                if char in guild.members:
                    guild.reputation += 10
                    for quest in char.active_quests:
                        if "guild_victory" in quest.objectives and guild in [
                            self.teams[f"Команда {1 if winner == team1 else 2}"][0].guild for c in winner]:
                            quest.update_progress("guild_victory")

        for character in self.characters:
            for stat, value in self.current_location.battle_modifiers.items():
                current_value = getattr(character, stat, 0)
                setattr(character, stat, current_value / (1 + value))
            for faction in self.factions:
                if character.reputation[faction.name] >= 50 and faction.relations.get("Лицарі", 0.5) >= 0.8:
                    for stat, value in faction.bonuses.items():
                        if stat != "discount":
                            current_value = getattr(character, stat, 0)
                            setattr(character, stat, current_value / (1 + value))

        self.day += 1
        self.trigger_event()

    def trade(self):
        if len(self.characters) < 2:
            print("Потрібно щонайменше 2 персонажа для торгівлі!")
            return
        print("\nВибір першого персонажа:")
        for i, char in enumerate(self.characters, 1):
            print(f"{i}. {char.nickname}")
        try:
            char1_idx = int(input("Виберіть першого персонажа: ")) - 1
            if not (0 <= char1_idx < len(self.characters)):
                print("Некоректний вибір!")
                return
            char1 = self.characters[char1_idx]
            print("\nВибір другого персонажа:")
            for i, char in enumerate(self.characters, 1):
                if char != char1:
                    print(f"{i}. {char.nickname}")
            char2_idx = int(input("Виберіть другого персонажа: ")) - 1
            if not (0 <= char2_idx < len(self.characters) and self.characters[char2_idx] != char1):
                print("Некоректний вибір!")
                return
            char2 = self.characters[char2_idx]
            print(f"\nІнвентар {char1.nickname}:")
            for i, item in enumerate(char1.inventory, 1):
                print(f"{i}. {item}")
            item1_idx = int(input("Виберіть предмет від першого персонажа (0 для скасування): ")) - 1
            if item1_idx == -1:
                return
            if not (0 <= item1_idx < len(char1.inventory)):
                print("Некоректний вибір!")
                return
            print(f"\nІнвентар {char2.nickname}:")
            for i, item in enumerate(char2.inventory, 1):
                print(f"{i}. {item}")
            item2_idx = int(input("Виберіть предмет від другого персонажа (0 для скасування): ")) - 1
            if item2_idx == -1:
                return
            if not (0 <= item2_idx < len(char2.inventory)):
                print("Некоректний вибір!")
                return
            item1 = char1.inventory.pop(item1_idx)
            item2 = char2.inventory.pop(item2_idx)
            char1.inventory.append(item2)
            char2.inventory.append(item1)
            print(f"{char1.nickname} і {char2.nickname} обмінялися предметами: {item1.name} ↔ {item2.name}")
        except (ValueError, EOFError):
            print("Помилка введення. Торгівля скасована.")

    def set_difficulty(self):
        try:
            difficulty = int(input("Введіть рівень складності (1-10): "))
            if 1 <= difficulty <= 10:
                self.difficulty = difficulty
                print(f"Рівень складності встановлено: {self.difficulty}")
            else:
                print("Складність має бути від 1 до 10!")
        except (ValueError, EOFError):
            print("Помилка введення. Складність не змінено.")

    def set_location(self):
        print("\nДоступні локації:")
        for i, location in enumerate(self.locations, 1):
            print(f"{i}. {location.name}: {location.description}")
        try:
            choice = int(input("Виберіть локацію: ")) - 1
            if 0 <= choice < len(self.locations):
                self.current_location = self.locations[choice]
                print(f"Поточна локація: {self.current_location.name}")
            else:
                print("Некоректний вибір!")
        except (ValueError, EOFError):
            print("Помилка введення. Локація не змінена.")

    def manage_guilds(self):
        print("\nУправління гільдіями:")
        print("1. Створити гільдію")
        print("2. Додати персонажа до гільдії")
        print("3. Видалити персонажа з гільдії")
        print("4. Переглянути гільдії")
        print("0. Вийти")
        try:
            choice = int(input("Виберіть дію: "))
            if choice == 1:
                name = input("Введіть назву гільдії: ")
                if name.strip():
                    self.guilds.append(Guild(name))
                    print(f"Гільдію {name} створено!")
                else:
                    print("Назва не може бути порожньою!")
            elif choice == 2:
                if not self.characters:
                    print("Немає персонажів!")
                    return
                if not self.guilds:
                    print("Немає гільдій!")
                    return
                print("\nВибір гільдії:")
                for i, guild in enumerate(self.guilds, 1):
                    print(f"{i}. {guild.name}")
                guild_idx = int(input("Виберіть гільдію: ")) - 1
                if not (0 <= guild_idx < len(self.guilds)):
                    print("Некоректний вибір!")
                    return
                guild = self.guilds[guild_idx]
                print("\nВибір персонажа:")
                available_chars = [c for c in self.characters if c not in guild.members]
                for i, char in enumerate(available_chars, 1):
                    print(f"{i}. {char.nickname}")
                char_idx = int(input("Виберіть персонажа: ")) - 1
                if 0 <= char_idx < len(available_chars):
                    guild.add_member(available_chars[char_idx])
                else:
                    print("Некоректний вибір!")
            elif choice == 3:
                if not self.guilds:
                    print("Немає гільдій!")
                    return
                print("\nВибір гільдії:")
                for i, guild in enumerate(self.guilds, 1):
                    print(f"{i}. {guild.name}")
                guild_idx = int(input("Виберіть гільдію: ")) - 1
                if not (0 <= guild_idx < len(self.guilds)):
                    print("Некоректний вибір!")
                    return
                guild = self.guilds[guild_idx]
                if not guild.members:
                    print("Гільдія порожня!")
                    return
                print("\nВибір персонажа:")
                for i, char in enumerate(guild.members, 1):
                    print(f"{i}. {char.nickname}")
                char_idx = int(input("Виберіть персонажа: ")) - 1
                if 0 <= char_idx < len(guild.members):
                    guild.remove_member(guild.members[char_idx])
                else:
                    print("Некоректний вибір!")
            elif choice == 4:
                for guild in self.guilds:
                    print(f"\nГільдія {guild.name} (Репутація: {guild.reputation}):")
                    for member in guild.members:
                        print(f"  {member.nickname}")
            elif choice == 0:
                return
            else:
                print("Некоректний вибір!")
        except (ValueError, EOFError):
            print("Помилка введення. Управління гільдіями скасовано.")

    def show_reputation(self):
        if not self.characters:
            print("Немає персонажів!")
            return
        print("\nВибір персонажа:")
        for i, char in enumerate(self.characters, 1):
            print(f"{i}. {char.nickname}")
        try:
            char_idx = int(input("Виберіть персонажа: ")) - 1
            if 0 <= char_idx < len(self.characters):
                char = self.characters[char_idx]
                print(f"\nРепутація {char.nickname}:")
                for faction, value in char.reputation.items():
                    print(f"  {faction}: {value}")
            else:
                print("Некоректний вибір!")
        except (ValueError, EOFError):
            print("Помилка введення. Перегляд репутації скасовано.")

    def manage_factions(self):
        print("\nУправління фракціями:")
        print("1. Переглянути відносини")
        print("2. Укласти союз")
        print("3. Оголосити війну")
        print("0. Вийти")
        try:
            choice = int(input("Виберіть дію: "))
            if choice == 1:
                for faction in self.factions:
                    print(f"\nФракція {faction.name}:")
                    for other_faction, relation in faction.relations.items():
                        status = "Союзники" if relation >= 0.8 else "Вороги" if relation <= 0.2 else "Нейтральні"
                        print(f"  {other_faction}: {relation:.2f} ({status})")
            elif choice == 2:
                print("\nВибір фракції:")
                for i, faction in enumerate(self.factions, 1):
                    print(f"{i}. {faction.name}")
                faction_idx = int(input("Виберіть фракцію: ")) - 1
                if not (0 <= faction_idx < len(self.factions)):
                    print("Некоректний вибір!")
                    return
                faction = self.factions[faction_idx]
                print("\nВибір фракції для союзу:")
                for i, other_faction in enumerate(self.factions, 1):
                    if other_faction != faction:
                        print(f"{i}. {other_faction.name}")
                other_idx = int(input("Виберіть фракцію: ")) - 1
                if not (0 <= other_idx < len(self.factions) and self.factions[other_idx] != faction):
                    print("Некоректний вибір!")
                    return
                faction.update_relations(self.factions[other_idx].name, 0.2)
                self.factions[other_idx].update_relations(faction.name, 0.2)
                for char in self.characters:
                    for quest in char.active_quests:
                        if "max_relations" in quest.objectives and faction.relations[
                            self.factions[other_idx].name] >= 1.0:
                            quest.update_progress("max_relations")
            elif choice == 3:
                print("\nВибір фракції:")
                for i, faction in enumerate(self.factions, 1):
                    print(f"{i}. {faction.name}")
                faction_idx = int(input("Виберіть фракцію: ")) - 1
                if not (0 <= faction_idx < len(self.factions)):
                    print("Некоректний вибір!")
                    return
                faction = self.factions[faction_idx]
                print("\nВибір фракції для війни:")
                for i, other_faction in enumerate(self.factions, 1):
                    if other_faction != faction:
                        print(f"{i}. {other_faction.name}")
                other_idx = int(input("Виберіть фракцію: ")) - 1
                if not (0 <= other_idx < len(self.factions) and self.factions[other_idx] != faction):
                    print("Некоректний вибір!")
                    return
                faction.update_relations(self.factions[other_idx].name, -0.3)
                self.factions[other_idx].update_relations(faction.name, -0.3)
            elif choice == 0:
                return
            else:
                print("Некоректний вибір!")
        except (ValueError, EOFError):
            print("Помилка введення. Управління фракціями скасовано.")

    def start_guild_war(self):
        if len(self.guilds) < 2:
            print("Потрібно щонайменше 2 гільдії для війни!")
            return
        print("\nВибір першої гільдії:")
        for i, guild in enumerate(self.guilds, 1):
            print(f"{i}. {guild.name}")
        try:
            guild1_idx = int(input("Виберіть першу гільдію: ")) - 1
            if not (0 <= guild1_idx < len(self.guilds)):
                print("Некоректний вибір!")
                return
            guild1 = self.guilds[guild1_idx]
            print("\nВибір другої гільдії:")
            for i, guild in enumerate(self.guilds, 1):
                if guild != guild1:
                    print(f"{i}. {guild.name}")
            guild2_idx = int(input("Виберіть другу гільдію: ")) - 1
            if not (0 <= guild2_idx < len(self.guilds) and self.guilds[guild2_idx] != guild1):
                print("Некоректний вибір!")
                return
            guild2 = self.guilds[guild2_idx]
            stakes = {
                "gold": float(input("Введіть ставку золота: ")),
                "exp": float(input("Введіть ставку досвіду: ")),
                "reputation": float(input("Введіть ставку репутації: "))
            }
            war = GuildWar(guild1, guild2, stakes)
            self.guild_wars.append(war)
            war.resolve_war(self)
        except (ValueError, EOFError):
            print("Помилка введення. Війна скасована.")

    def apply_elemental_combo(self, character: Character, targets: List[Character], used_elements: List[DamageType]):
        for effect in self.elemental_effects:
            if all(elem in used_elements for elem in effect.elements):
                for target in targets:
                    target.apply_effect(effect.effect)
                    print(f"Комбінація стихій: {effect.name} на {target.nickname}!")

    def trigger_event(self):
        if random.random() < 0.3:
            event = random.choice(self.events)
            print(f"\nПодія: {event.name}")
            print(event.description)
            event.effect(self)
        if random.random() < 0.2:
            self.trigger_dynamic_event()

    def trigger_dynamic_event(self):
        valid_events = [event for event in self.dynamic_events if event.can_trigger(self)]
        if not valid_events:
            print("Немає доступних подій!")
            return
        event = random.choice(valid_events)
        print(f"\nПодія: {event.name}")
        print(event.description)
        event.effect(self)

    def craft_item(self):
        if not self.characters:
            print("Немає персонажів!")
            return
        print("\nВибір персонажа:")
        for i, char in enumerate(self.characters, 1):
            print(f"{i}. {char.nickname}")
        try:
            char_idx = int(input("Виберіть персонажа: ")) - 1
            if not (0 <= char_idx < len(self.characters)):
                print("Некоректний вибір!")
                return
            character = self.characters[char_idx]
            print("\nДоступні рецепти:")
            for i, recipe in enumerate(self.crafting_recipes, 1):
                print(
                    f"{i}. {recipe.name} (Потрібно: {', '.join(f'{k}: {v}' for k, v in recipe.required_items.items())})")
            recipe_idx = int(input("Виберіть рецепт: ")) - 1
            if not (0 <= recipe_idx < len(self.crafting_recipes)):
                print("Некоректний вибір!")
                return
            recipe = self.crafting_recipes[recipe_idx]
            if recipe.can_craft(character.inventory):
                recipe.craft(character)
            else:
                print("Недостатньо матеріалів!")
        except (ValueError, EOFError):
            print("Помилка введення. Крафт скасовано.")

    def save_game(self, filename="game_save.json"):
        try:
            game_state = {
                "characters": [char.to_dict() for char in self.characters],
                "teams": {k: [char.nickname for char in team] for k, team in self.teams.items()},
                "quests": [quest.to_dict() for quest in self.quests],
                "weather_system": self.weather_system.to_dict(),
                "current_round": self.current_round,
                "day": self.day,
                "difficulty": self.difficulty,
                "current_location": self.current_location.to_dict() if self.current_location else None,
                "guilds": [guild.to_dict() for guild in self.guilds],
                "factions": [faction.to_dict() for faction in self.factions],
                "guild_wars": [war.to_dict() for war in self.guild_wars],
                "elemental_effects": [effect.to_dict() for effect in self.elemental_effects],
                "dynamic_events": [event.to_dict() for event in self.dynamic_events],
                "crafting_recipes": [recipe.to_dict() for recipe in self.crafting_recipes]
            }
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(game_state, f, ensure_ascii=False, indent=2)
            print(f"Гру збережено у файл {filename}!")
        except Exception as e:
            print(f"Помилка при збереженні гри: {e}")

    def load_game(self, filename="game_save.json"):
        try:
            if not os.path.exists(filename):
                print(f"Файл збереження {filename} не знайдено!")
                return False
            with open(filename, 'r', encoding='utf-8') as f:
                game_state = json.load(f)

            self.characters = [Character.from_dict(char) for char in game_state["characters"]]
            self.teams = {
                k: [next(c for c in self.characters if c.nickname == nick) for nick in team]
                for k, team in game_state["teams"].items()
            }
            self.quests = [Quest.from_dict(quest) for quest in game_state["quests"]]
            for char in self.characters:
                char.active_quests = [next(q for q in self.quests if q.id == qid) for qid in
                                      char.to_dict()["active_quests"]]
            self.weather_system.from_dict(game_state["weather_system"])
            self.current_round = game_state["current_round"]
            self.day = game_state["day"]
            self.difficulty = game_state["difficulty"]
            self.current_location = Location.from_dict(game_state["current_location"]) if game_state[
                "current_location"] else self.locations[0]
            self.guilds = [Guild.from_dict(guild) for guild in game_state["guilds"]]
            for guild, guild_data in zip(self.guilds, game_state["guilds"]):
                guild.members = [next(c for c in self.characters if c.nickname == nick) for nick in
                                 guild_data["members"]]
            self.factions = [Faction.from_dict(faction) for faction in game_state["factions"]]
            self.guild_wars = [GuildWar.from_dict(war, self.guilds) for war in game_state["guild_wars"]]
            self.elemental_effects = [ElementalEffect.from_dict(effect) for effect in game_state["elemental_effects"]]
            self.dynamic_events = [DynamicEvent.from_dict(event) for event in game_state["dynamic_events"]]
            self.crafting_recipes = [CraftingRecipe.from_dict(recipe) for recipe in game_state["crafting_recipes"]]

            print(f"Гру завантажено з файлу {filename}!")
            return True
        except Exception as e:
            print(f"Помилка при завантаженні гри: {e}")
            return False

    def main_menu(self):
        while True:
            print("\nГоловне меню:")
            print("1. Створити персонажа")
            print("2. Переглянути персонажів")
            print("3. Магазин")
            print("4. Формування команд")
            print("5. Почати битву")
            print("6. Активні квести")
            print("7. Виконати кілька команд")
            print("8. Зберегти гру")
            print("9. Завантажити гру")
            print("10. Торгівля між персонажами")
            print("11. Встановити рівень складності")
            print("12. Вибір локації")
            print("13. Управління гільдіями")
            print("14. Переглянути репутацію")
            print("15. Управління фракціями")
            print("16. Почати гільдійську війну")
            print("17. Викликати подію")
            print("18. Крафт предметів")
            print("0. Вийти")
            try:
                choice = int(input("Виберіть опцію: "))
                if choice == 0:
                    print("Вихід з гри.")
                    break
                elif choice == 1:
                    self.create_character()
                elif choice == 2:
                    if not self.characters:
                        print("Немає створених персонажів!")
                        continue
                    print("\nСписок персонажів:")
                    for i, character in enumerate(self.characters, 1):
                        print(f"{i}. {character}")
                    try:
                        char_choice = int(input("Виберіть персонажа для деталей (0 для скасування): ")) - 1
                        if 0 <= char_choice < len(self.characters):
                            self.show_character_status(self.characters[char_choice])
                    except (ValueError, EOFError):
                        print("Помилка введення. Пропуск.")
                elif choice == 3:
                    if not self.characters:
                        print("Спочатку створіть персонажа!")
                        continue
                    print("\nВибір персонажа для магазину:")
                    for i, character in enumerate(self.characters, 1):
                        print(f"{i}. {character.nickname} ({character.gold} золота)")
                    try:
                        char_choice = int(input("Виберіть персонажа (0 для скасування): ")) - 1
                        if 0 <= char_choice < len(self.characters):
                            self.shop(self.characters[char_choice])
                    except (ValueError, EOFError):
                        print("Помилка введення. Пропуск.")
                elif choice == 4:
                    if len(self.characters) < 2:
                        print("Потрібно мінімум 2 персонажа!")
                        continue
                    self.team_selection()
                elif choice == 5:
                    if len(self.teams) < 2 or any(len(team) < 1 for team in self.teams.values()):
                        print("Сформуйте щонайменше 2 команди з персонажами!")
                        continue
                    self.battle()
                elif choice == 6:
                    if not self.characters:
                        print("Немає персонажів!")
                        continue
                    print("\nВибір персонажа:")
                    for i, character in enumerate(self.characters, 1):
                        print(f"{i}. {character.nickname}")
                    try:
                        char_idx = int(input("Виберіть персонажа: ")) - 1
                        if 0 <= char_idx < len(self.characters):
                            character = self.characters[char_idx]
                            if not character.active_quests:
                                print("Немає активних квестів!")
                                continue
                            print(f"\nАктивні квести для {character.nickname}:")
                            for quest in character.active_quests:
                                print(f"- {quest.title}: {quest.description}")
                                for obj, goal in quest.objectives.items():
                                    print(f"  Прогрес: {quest.progress[obj]}/{goal}")
                        else:
                            print("Некоректний вибір!")
                    except (ValueError, EOFError):
                        print("Помилка введення. Пропуск.")
                elif choice == 7:
                    self.execute_multiple_commands()
                elif choice == 8:
                    self.save_game()
                elif choice == 9:
                    self.load_game()
                elif choice == 10:
                    self.trade()
                elif choice == 11:
                    self.set_difficulty()
                elif choice == 12:
                    self.set_location()
                elif choice == 13:
                    self.manage_guilds()
                elif choice == 14:
                    self.show_reputation()
                elif choice == 15:
                    self.manage_factions()
                elif choice == 16:
                    self.start_guild_war()
                elif choice == 17:
                    self.trigger_dynamic_event()
                elif choice == 18:
                    self.craft_item()
                else:
                    print("Некоректний вибір!")
            except (ValueError, EOFError):
                print("Помилка введення. Спробуйте ще раз.")

    def execute_multiple_commands(self):
        print("\nВиконання кількох команд:")
        commands = []
        print("Введіть команди (наприклад: shop 1, battle, exit). Введіть порожній рядок для завершення:")
        while True:
            try:
                cmd = input("Команда: ").strip()
                if not cmd:
                    break
                commands.append(cmd)
            except (EOFError, KeyboardInterrupt):
                print("Введення команд завершено.")
                break

        for cmd in commands:
            try:
                parts = cmd.split()
                if not parts:
                    continue
                command = parts[0].lower()
                args = parts[1:]

                if command == "shop" and len(args) == 1:
                    char_idx = int(args[0]) - 1
                    if 0 <= char_idx < len(self.characters):
                        self.shop(self.characters[char_idx])
                    else:
                        print(f"Некоректний індекс персонажа: {args[0]}")
                elif command == "battle":
                    if len(self.teams) >= 2 and all(len(team) > 0 for team in self.teams.values()):
                        self.battle()
                    else:
                        print("Недостатньо команд для битви!")
                elif command == "create":
                    self.create_character()
                elif command == "status" and len(args) == 1:
                    char_idx = int(args[0]) - 1
                    if 0 <= char_idx < len(self.characters):
                        self.show_character_status(self.characters[char_idx])
                    else:
                        print(f"Некоректний індекс персонажа: {args[0]}")
                elif command == "trade":
                    self.trade()
                elif command == "difficulty" and len(args) == 1:
                    difficulty = int(args[0])
                    if 1 <= difficulty <= 10:
                        self.difficulty = difficulty
                        print(f"Рівень складності встановлено: {self.difficulty}")
                    else:
                        print("Складність має бути від 1 до 10!")
                elif command == "location" and len(args) == 1:
                    loc_idx = int(args[0]) - 1
                    if 0 <= loc_idx < len(self.locations):
                        self.current_location = self.locations[loc_idx]
                        print(f"Поточна локація: {self.current_location.name}")
                    else:
                        print(f"Некоректний індекс локації: {args[0]}")
                elif command == "guild":
                    self.manage_guilds()
                elif command == "reputation":
                    self.show_reputation()
                elif command == "faction":
                    self.manage_factions()
                elif command == "war":
                    self.start_guild_war()
                elif command == "event":
                    self.trigger_dynamic_event()
                elif command == "craft":
                    self.craft_item()
                elif command == "save":
                    self.save_game()
                elif command == "load":
                    self.load_game()
                elif command == "quest" and len(args) == 1:
                    char_idx = int(args[0]) - 1
                    if 0 <= char_idx < len(self.characters):
                        character = self.characters[char_idx]
                        if not character.active_quests:
                            print("Немає активних квестів!")
                        else:
                            print(f"\nАктивні квести для {character.nickname}:")
                            for quest in character.active_quests:
                                print(f"- {quest.title}: {quest.description}")
                                for obj, goal in quest.objectives.items():
                                    print(f"  Прогрес: {quest.progress[obj]}/{goal}")
                    else:
                        print(f"Некоректний індекс персонажа: {args[0]}")
                elif command == "exit":
                    print("Вихід із виконання команд.")
                    break
                else:
                    print(f"Невідома команда: {cmd}")
            except (ValueError, EOFError):
                print(f"Помилка обробки команди: {cmd}")

    def manage_quests(self, character: Character):
        print(f"\nУправління квестами для {character.nickname}:")
        print("1. Взяти квест")
        print("2. Переглянути активні квести")
        print("3. Завершити квест")
        print("0. Вийти")
        try:
            choice = int(input("Виберіть дію: "))
            if choice == 0:
                return
            elif choice == 1:
                available_quests = [q for q in self.quests if q not in character.active_quests]
                if not available_quests:
                    print("Немає доступних квестів!")
                    return
                print("\nДоступні квести:")
                for i, quest in enumerate(available_quests, 1):
                    print(f"{i}. {quest.title}: {quest.description}")
                quest_idx = int(input("Виберіть квест: ")) - 1
                if 0 <= quest_idx < len(available_quests):
                    character.active_quests.append(available_quests[quest_idx])
                    print(f"{character.nickname} взяв квест '{available_quests[quest_idx].title}'!")
                else:
                    print("Некоректний вибір!")
            elif choice == 2:
                if not character.active_quests:
                    print("Немає активних квестів!")
                    return
                print("\nАктивні квести:")
                for quest in character.active_quests:
                    print(f"- {quest.title}: {quest.description}")
                    for obj, goal in quest.objectives.items():
                        print(f"  Прогрес: {quest.progress[obj]}/{goal}")
            elif choice == 3:
                if not character.active_quests:
                    print("Немає активних квестів!")
                    return
                print("\nАктивні квести:")
                for i, quest in enumerate(character.active_quests, 1):
                    print(f"{i}. {quest.title}: {quest.description}")
                quest_idx = int(input("Виберіть квест для завершення: ")) - 1
                if 0 <= quest_idx < len(character.active_quests):
                    quest = character.active_quests[quest_idx]
                    if quest.is_completed():
                        character.gold += quest.rewards.get("gold", 0)
                        character.add_exp(quest.rewards.get("exp", 0))
                        if "item" in quest.rewards:
                            character.inventory.append(quest.rewards["item"])
                        print(
                            f"Квест '{quest.title}' завершено! Нагороди: {quest.rewards.get('gold', 0)} золота, {quest.rewards.get('exp', 0)} досвіду")
                        if "item" in quest.rewards:
                            print(f"Отримано предмет: {quest.rewards['item']}")
                        character.active_quests.pop(quest_idx)
                    else:
                        print("Квест ще не виконано!")
                else:
                    print("Некоректний вибір!")
            else:
                print("Некоректний вибір!")
        except (ValueError, EOFError):
            print("Помилка введення. Управління квестами скасовано.")

    def upgrade_skill(self, character: Character):
        print(f"\nПрокачування навичок для {character.nickname}:")
        if not character.skills:
            print("Немає доступних навичок!")
            return
        print("Доступні навички:")
        for i, skill in enumerate(character.skills, 1):
            print(f"{i}. {skill} (Рівень {character.skill_levels[skill]})")
        try:
            skill_idx = int(input("Виберіть навичку для прокачування: ")) - 1
            if 0 <= skill_idx < len(character.skills):
                skill = character.skills[skill_idx]
                cost = character.skill_levels[skill] * 50
                if character.gold >= cost:
                    character.gold -= cost
                    character.skill_levels[skill] += 1
                    print(f"Навичка {skill} прокачана до рівня {character.skill_levels[skill]} за {cost} золота!")
                else:
                    print(f"Недостатньо золота! Потрібно: {cost}")
            else:
                print("Некоректний вибір!")
        except (ValueError, EOFError):
            print("Помилка введення. Прокачування скасовано.")

    def check_achievements(self, character: Character):
        achievements = [
            ("Майстер бою", lambda c: c.level >= 5, {"exp": 100, "gold": 50}),
            ("Легендарний колекціонер",
             lambda c: sum(1 for item in c.inventory if item.quality == ItemQuality.LEGENDARY) >= 3,
             {"exp": 200, "item": Item("Легендарний амулет", ItemType.ACCESSORY, 15, 300, ItemQuality.LEGENDARY)}),
            ("Герой гільдії", lambda c: any(c in guild.members and guild.reputation >= 100 for guild in self.guilds),
             {"gold": 300}),
            ("Миротворець", lambda c: any(faction.relations.get("Лицарі", 0) >= 0.9 for faction in self.factions),
             {"exp": 150, "gold": 200})
        ]
        print(f"\nДосягнення для {character.nickname}:")
        for name, condition, rewards in achievements:
            if condition(character):
                print(f"Досягнення '{name}' виконано!")
                character.add_exp(rewards.get("exp", 0))
                character.gold += rewards.get("gold", 0)
                if "item" in rewards:
                    character.inventory.append(rewards["item"])
                    print(f"Отримано предмет: {rewards['item']}")
            else:
                print(f"Досягнення '{name}' ще не виконано.")

    def run(self):
        print("Ласкаво просимо до гри!")
        while True:
            self.main_menu()
            if not any(input("Натисніть Enter для продовження або 'q' для виходу: ").lower() == 'q' for _ in [1]):
                continue
            break


if __name__ == "__main__":
    game = Game()
    game.run()