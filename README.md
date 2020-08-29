# gnp_pygame - personal PyGame utilities

A library that contains a collection of [PyGame](https://www.pygame.org/) utilities I wrote many years ago,
early in my Python journey.  They are generally poorly written and structured.
But, they have a couple good ideas and used in a game or two of mine.  So, here
they are:

- `gnipMath.py`: 2D/3D vectors, lerp, trig, range, polar coordinates, bare-bones matrix operations
- `gnpcollision.py`: Initial palceholder implementations of a few collision math routines
- `gnppygame.py`: `Game` and `GameWithStates` (state machines that drives a games flow), PyGame helpers (fonts, timers, audio, frame delta, joystick), `Actor` (game objects with lifetime) and `ActorList` classes
- `gnpactor.py`: a collection of ready-to-use `Actor` subclasses
- `gnpinput.py`: logic to synthesize higher-level input features (holds, joystick axis-presses)
- `gnpparticle.py`: Particle systems library, provides `Emitter` and `Particle` classes along with a number of pre-build `Emitter` subclasses 


# Installation

## ...for use

    pip install git+https://github.com/SirGnip/gnp_pygame.git
    
## ...for development

    # Open a GitBash shell
    git clone https://github.com/SirGnip/gnp_pygame.git
    cd gnp_pygame
    py -2 -m virtualenv venv
    source venv/Scripts/activate
    pip install -e .


# Running tests

    # doctests
    pytest --doctest-module --verbose
    
    # unittest-based tests
    pytest --pyargs gnp_pygame.gnpinput --verbose
    
    # interactive demo/smoke test that exercises a lot of code in gnppygame
    python -m gnp_pygame.gnppygame

(Note: The pytest tool is used solely for its ability to discover and run
both doctests and unittest based tests. No tests are (currently) written
using the pytest format.)

