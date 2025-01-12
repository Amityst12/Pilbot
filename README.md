# Pilbot - A Discord Bot for TFT Players

Pilbot is a Discord bot designed to provide valuable insights and tools for Teamfight Tactics (TFT) players. Whether you're tracking your stats, checking unit details, or calculating odds, Pilbot has got you covered.

---

## Features

- **TFT Profile Lookup**  
  Check a player's profile, including rank and game mode stats.  
  Command: `TFT profile (playerID) (playerTAG)`

- **Unit Information**  
  Get detailed stats for any TFT unit.  
  Command: `TFT unit (Unit Name)`

- **Match History**  
  Retrieve the last few matches for a player.  
  Command: `TFT history (playerID) (playerTAG) (1-10)`

- **Ongoing Game Data**  
  See live stats for a player's current game.  
  Command: `TFT ingame (playerID) (playerTAG)`

- **Odds Calculator**  
  Calculate pool odds and unit probabilities.  
  Command: `TFT pool`, `TFT odds`

---

## How to Use Pilbot

1. Add Pilbot to your Discord server.
2. Type `TFT (command name)` to execute a command.
   - Example: `TFT profile Lucario EUNE`
   - Example: `TFT help`

### Important Notes
- Player ID should not contain spaces.
- Currently supports EU players only.

---

## Installation

If you'd like to run Pilbot locally or contribute to its development:

1. Clone the repository:
   ```bash
   git clone https://github.com/Amityst12/Pilbot
   ```
2. Navigate to the project directory:
   ```bash
   cd Main.py
   ```
3. Install the required dependencies:
   ```bash
   pip install discord.py
   pip install requests
   pip install python-dotenv
   pip install numpy
   
   ```
4. Set up your environment variables in a `.env` file:
   ```env
   RIOT_API_KEY=your_riot_api_key
   DISCORD_BOT_TOKEN=your_discord_bot_token
   ```
5. Run the bot:
   ```bash
   python main.py
   ```

---

## Contributing

Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add your message here"
   ```
4. Push to your branch:
   ```bash
   git push origin feature/your-feature-name
   ```
5. Open a pull request.

---

## License

This project is licensed under the MIT License file.

---

## Acknowledgments

Pilbot was created by Amityst12 using Riot's API.
Special thanks to the TFT community for their feedback and support.

---

## Contact

For support or inquiries, feel free to open an issue on GitHub or contact me on Discord.
