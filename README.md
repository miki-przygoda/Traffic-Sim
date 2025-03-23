# 🚗 Randomized Car Generation (Pygame)

This project simulates randomized car generation and movement using **Pygame**, a popular Python library for game development and simple simulations.

Built as a personal exploration into basic simulation logic, object tracking, and graphical event loops, this project helped me explore collision mechanics, randomness, and visual object lifecycles in a 2D space.

---

## 🧩 Features

- Real-time simulation of cars appearing at random horizontal positions
- Simple grid-based movement and window-based rendering
- Basic object lifetime and redraw logic using Pygame's main loop
- Fully customizable spawn rate, car size, speed, and screen dimensions

---

## 🎮 Controls & Customization

- Simulation starts automatically when `main.py` is run
- Parameters like window size, car speed, and spawn intervals can be changed in `main.py`

Example:

```python
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
SPAWN_RATE = 25  # Lower = faster spawns
```

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/miki-przygoda/random-car-sim.git
cd random-car-sim
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the simulation

```bash
python main.py
```

---

## 📦 Requirements

- Python 3.10+
- pygame

All required libraries are listed in `requirements.txt`

---

## 🧠 Future Ideas

- Main improvement -- making the cars acutally turn properly...
- Collision detection between cars
- More realistic car shapes and spawn angles
- Interactive UI elements (start/stop button, car counter)
- Score or stat tracking over time

---

## ✍️ Author

**Mikolaj Mikuliszyn**  
Personal AI & Simulation Projects  
🔗 [GitHub Profile](https://github.com/miki-przygoda)

---

## 📝 License

This project is shared under the MIT License. Free to use, modify, or build upon.
