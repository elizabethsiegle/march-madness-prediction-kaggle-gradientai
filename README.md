# March Madness Predictor 🏀

LLM-powered March Madness bracket predictions with personalized team analysis using [historical March Madness data from Kaggle](https://www.kaggle.com/competitions/march-machine-learning-mania-2026/data)

## Quick Start
Get your Model Access Key at [DigitalOcean's Agent Platform](https://cloud.digitalocean.com/gen-ai/model-access-keys?i=760f86) and [Kaggle API Token](https://www.kaggle.com/settings) so you can use the CLI to parse the Kaggle March Madness data! 🚀

1. **Set up your API key:**
   ```bash
   echo "MODEL_ACCESS_KEY=your-gradient-api-key" > .env
   ```

2. **Run the predictor:**
   ```bash
   ./env/bin/python3 predictor.py
   ```

That's it! Choose your favorite teams and risk level, then get your personalized bracket predictions.

## What it does

- 📊 Analyzes NCAA tournament data 
- 🎯 Considers your favorite teams
- 🎲 Adjusts predictions based on your risk tolerance
- 🤖 Uses AI to generate bracket picks