# Match Joy

Match Joy is a simple match-3 puzzle game built with Python and Pygame. It demonstrates the core gameplay loop of a casual tile-matching game: swapping adjacent blocks, detecting matches, clearing tiles, dropping remaining blocks, filling new blocks, scoring, and ending the game when moves run out.

The project also includes scripts for building and running a web version with pygbag, so the game can be played in a browser or deployed with GitHub Pages.

## Features

- 8x8 match-3 game board
- Click two adjacent blocks to swap them
- Automatic match detection for rows and columns
- Tile clearing, falling, and refill logic
- Score counter
- Limited moves system
- Pop, spawn, cascade, and screen shake effects
- Desktop version powered by Pygame
- Browser build support through pygbag

## Project Structure

```text
.
├── main.py                  # Game entry point
├── test.py                  # Main game logic
├── images/                  # Tile image assets
├── build_web.sh             # Build the browser version
├── run_web.sh               # Run the built browser version locally
├── deploy_github_pages.sh   # Prepare files for GitHub Pages
├── WEB_BUILD.md             # Web build guide
└── WEB_DEPLOY.md            # GitHub Pages deployment guide
```

## Run Locally

Install Pygame first:

```bash
pip install pygame
```

Then start the desktop game:

```bash
python main.py
```

If your system uses `python3` instead of `python`, run:

```bash
python3 main.py
```

## Run Web Version

Build the web version:

```bash
bash build_web.sh
```

Start a local web server:

```bash
bash run_web.sh
```

Open the game in your browser:

```text
http://localhost:8000/index.html
```

If port `8000` is already in use, choose another port:

```bash
PORT=8888 bash run_web.sh
```

## Deploy to GitHub Pages

Generate the deployment files:

```bash
bash deploy_github_pages.sh
```

Then commit and push the generated `docs/` directory:

```bash
git add docs
git commit -m "deploy web build"
git push
```

In the GitHub repository settings, enable GitHub Pages with:

- Source: `main`
- Folder: `/docs`

## Notes

This is a learning/demo project focused on the basic mechanics of a match-3 game. It is not intended to be a full commercial game, but it is a good starting point for experimenting with puzzle game logic, animations, scoring rules, and browser deployment.
