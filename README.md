# Origami Diagram

## Brief Introduction

The project aims to make an app to draw origami diagrams just like folding a real paper.

## Current features

**For short, there is in fact no available feature.**

- load .fold file and render the cp. (NOTE: fixing)

## Development

Drawing origami diagrams is hard and there seems no sufficient theory support. Currently the development follows a
3-phase plan.

### Phase 1: Fully copy flat-folder

Flat-Folder is a good base. It implements computing folded state, which is one of the core part.

### Phase 2: Explore some new theories

Diagrams are not strictly projections of folded states. They serves more as illustration, rather computation results.
Therefore, new approaches are needed.

### Phase3: Contain 3d, probably physics simulation

Diagrams involving expand the paper and not flat stages need this.

By the way, at the very beginning, I intended to implement the project with XPBD and cloth simulation, but it required too many particles to reach good visual effect and the collision remains an obstacle.

## References

### Flat Folder

https://github.com/origamimagiro/flat-folder

### Origami Simulator

https://origamisimulator.org/

It views origami models as kinematics systems where faces are rigid boards and creases are hinges. Thus the system can
be simulated by solving the constraint equations. However, collisions between faces are not included. In addition, the
system usually has many DOFs(degree of freedom), making it hard to manipulate the model.