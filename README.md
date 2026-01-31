# N-body-simulator
Interactive Solar System N-Body Gravity Simulator that allows users to add custom objects and observe the gravitational influence of every object on every other object simultaneously.

---

## Overview
It is a Python program that visualises the model of the solar system. It uses VPython for real-time graphics and CustomTkinter for the graphical user interface. Together, these libraries enable an interactive simulation where the Sun and planets (and any custom object) move under Newtonian gravity.

In this program, user can
1. Simulate Standard Solar System:
     At the beginning, all planets are placed at their aphelion positions with their corresponding aphelion velocities.
2. Add Custom Object on the Standard Model:
     The user can add a custom object with any mass, position, and velocity vector to the standard model. A Help button is also available for estimating mass, position, and velocity.
3. Manually configure Planets:
     The user can manually change the position and velocity vectors of the planets and add a custom object to evaluate its interactions in the solar system. A Help button is also available for estimating the mass, position, and velocity vector of each planet.

## Features
- Standard Solar System: Simulates all eight planets orbiting the Sun with (scaled) real-world data for masses, distances, and velocities. The planets are drawn as colored spheres with motion trails.

- Add Custom Object: You can add one extra object (e.g. a comet, asteroid or planet) by specifying its name, mass, radius, and initial position/velocity in a popup form. This object will then appear alongside the planets in the simulation.

- Manual Configuration: An advanced setup window lets you manually override each planet’s initial X/Y/Z position and velocity (leaving blank fields uses the default values). You can also define an additional custom object here.

## Physics-Based Motion
The simulation calculates motion based on **Newton's Law of Universal Gravitation**:

$$F = G \frac{m_1 m_2}{r^2}$$

The net acceleration $\vec{a}$ for each body is calculated by summing the gravitational vectors from all other bodies in the scene:

$$\vec{a}_i = \sum_{j \neq i} \frac{G m_j}{|\vec{r}_{ij}|^2} \hat{r}_{ij}$$

  The program uses Newton's Law of Gravitation to compute net acceleration and update velocities and positions on each timestep.

 
  It also conserves total momentum of the system by slightly adjusting the Sun's velocity which stabilizes the system.
  Only gravitational forces are considered.

## Requirements
* **Python:** 3.7 or newer
* **Libraries:** `vpython`, `customtkinter`

