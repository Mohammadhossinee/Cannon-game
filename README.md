# Cannon-game


# 🎯 Cannon Game

A **2D side-view artillery game** called **Cannon**, inspired by classic artillery games.  
This project is developed using the **Kivy framework** and is designed to run on any system with **Python 3** and **Kivy** installed.  

---

## 📌 Overview
The final exam project involves designing and implementing a 2D artillery game with customizable features.  

---

## 🕹️ Game Description
- **Single-player Game:** Control a cannon on the left side of the screen to hit a target on the right side.  
- **Player Controls:** Adjust elevation angle, muzzle velocity, and projectile type.  
- **Objective:** Hit the target with the least number of shots across multiple rounds.  
- **Projectiles:**  
  - **Bullet:** Affected by gravity, parabolic trajectory, impacts within a radius.  
  - **Bombshell:** Affected by gravity, parabolic trajectory, penetrates obstacles, larger radius.  
  - **Laser:** Not affected by gravity, linear trajectory, penetrates obstacles, impacts over distance.  

---

## ⚙️ Specifications
- **Screen Size:** Defined by `SCREEN_WIDTH` and `SCREEN_HEIGHT`.  
- **Time & Frame Rate:** Measured in seconds, with optional `FPS` customization.  

---

## 🧱 Obstacles
- **Rock:** Main destructible environment component.  
- **Bulletproof Mirror:** Reflects laser impulses, indestructible.  
- **Perpetio:** Similar to Rock, but indestructible.  
- **Optional Obstacles:**  
  - **Wormhole**  
  - **Gravitonio** (affects gravity)  
  - **Elastonio** (reflects projectiles)  

---

## 🎮 Game Functionalities
- Save/Load game state.  
- Hall of Fame.  
- Help Menu.  

---

## 🖼️ Visualization
- **Single-Screen Display:** Entire game field visible in a fixed window.  
- **Extended Field Option:** Scrolling to explore a larger game field or follow projectile trajectories.  

---

## 🔧 Constants
- **Screen Dimensions:** `SCREEN_WIDTH`, `SCREEN_HEIGHT`  
- **Frame Rate:** `FPS`  
- **Projectile Parameters:**  
  - `BULLET_MASS`, `BOMB_MASS`  
  - `BULLET_RADIUS`, `BOMB_RADIUS`  
  - `LASER_DIST`, `BOMB_DRILL`  
  - `LASER_IMPULSE`, `LASER_VEL`  

---

## 🚀 Flexibility
This project provides flexibility in game design through customizable constants, ensuring an **adaptable and engaging gameplay experience**.  

---
