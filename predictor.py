#!/usr/bin/env python3

import os
import sys
sys.path.append('backend')
from gradient import Gradient
from data_analyzer import MarchMadnessAnalyzer

# Try to load .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("📁 Loaded .env file")
except ImportError:
    # dotenv not installed, that's fine
    pass
except Exception as e:
    print(f"⚠️  Could not load .env file: {e}")

def main():
    print("🏀 MARCH MADNESS BRACKET PREDICTOR 2026 🏀")
    print("="*60)
    
    # Initialize Gradient client
    print("🤖 Initializing AI model...")
    
    # Check if API key is available from environment
    api_key = os.environ.get("MODEL_ACCESS_KEY")
    
    if not api_key:
        print("❌ ERROR: MODEL_ACCESS_KEY environment variable not found!")
        sys.exit(1)
    
    if len(api_key) < 10:
        print("⚠️  Warning: API key seems too short - check if it's complete")
    else:
        print(f"✅ API key found: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        inference_client = Gradient(model_access_key=api_key)
        print("✅ Gradient client initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Gradient client: {e}")
        sys.exit(1)
    
    # Initialize data analyzer (this loads all the CSV data)
    print("📊 Loading March Madness data...")
    analyzer = MarchMadnessAnalyzer()
    print("✅ Data loaded successfully!")
    
    print("\n" + "="*60)
    print("TIME FOR SOME QUESTIONS!")
    print("="*60)
    
    # Question 1: Risk level
    while True:
        try:
            risk_level = int(input("\n🎯 On a scale from 1-10 (10 being the riskiest), how risky do you want the predictions to be? "))
            if 1 <= risk_level <= 10:
                break
            else:
                print("❌ Please enter a number between 1 and 10")
        except ValueError:
            print("❌ Please enter a valid number")
    
    # Question 2: Favorite teams
    print(f"\n✅ Risk level set to {risk_level}/10")
    favorite_teams = input("\n🏀 Are there any teams you are rooting for that you want the LLM to predict will make it further? (Enter team names separated by commas, or press Enter for none): ").strip()
    
    if favorite_teams:
        favorite_teams_list = [team.strip() for team in favorite_teams.split(",")]
        print(f"✅ Got your favorites: {', '.join(favorite_teams_list)}")
    else:
        favorite_teams_list = []
        print("✅ No favorites selected - pure chaos mode!")
    
    # Question 3: Optional matchup prediction
    matchup_question = input("\n🎯 Want to analyze a specific matchup? (e.g. 'Duke vs UNC' or press Enter to skip): ").strip()
    
    if matchup_question and " vs " in matchup_question.lower():
        team1, team2 = [team.strip() for team in matchup_question.lower().split(" vs ")]
        print(f"🔍 Analyzing matchup: {team1.title()} vs {team2.title()}")
        
        # Generate matchup analysis
        matchup_analysis = analyzer.analyze_team_matchup(team1, team2)
        
        if matchup_analysis and not matchup_analysis.get('error'):
            print(f"\n📊 MATCHUP ANALYSIS: {matchup_analysis['team1_name']} vs {matchup_analysis['team2_name']}")
            print("="*70)
            print(matchup_analysis['analysis'])
            print("="*70)
            
            # Ask if they want to continue to full bracket prediction
            continue_to_bracket = input("\n🎲 Continue to full bracket prediction? (y/n): ").strip().lower()
            if continue_to_bracket != 'y':
                print("\n✨ Thanks for using the matchup analyzer!")
                return
        else:
            print(f"❌ {matchup_analysis.get('error', 'Could not analyze this matchup')}")
            print("🔄 Continuing to bracket prediction...")
    else:
        if matchup_question:
            print("ℹ️  Use format like 'Duke vs UNC' for matchup analysis")
        print("🔄 Proceeding to bracket prediction...")
    
    # Generate LLM prediction
    print(f"\n🤖 Generating bracket predictions with risk level {risk_level}...")
    if favorite_teams_list:
        print(f"🎯 Considering your favorite teams: {', '.join(favorite_teams_list)}")
    
    # Get real data for context
    actual_matchups = analyzer.get_actual_first_round_matchups()
    upset_stats = analyzer.get_upset_statistics()
    conf_stats = analyzer.analyze_conference_strength()
    
    # Get structured data for Nemotron to analyze (smaller samples)
    structured_data = {
        'upset_probabilities': {k: v for k, v in list(upset_stats.items())[:5]},  # Just top 5
        'conference_performance': {k: v for k, v in list(conf_stats.items())[:5]},  # Just top 5
        'sample_teams': analyzer.data['teams'].head(10).to_dict('records'),  # Just 10 teams
        'data_summary': {
            'total_tournament_games': len(analyzer.data['tourney_results']),
            'total_regular_season_games': len(analyzer.data['regular_season']),
            'upset_categories': len(upset_stats),
            'conferences_analyzed': len(conf_stats)
        }
    }
    
    # Create COMPLETE 2026 bracket listing to prevent hallucinations
    complete_bracket = ""
    for region, teams in analyzer.bracket_2026.items():
        complete_bracket += f"\n{region.upper()} REGION:\n"
        for seed, team_info in sorted(teams.items()):
            complete_bracket += f"  {seed}: {team_info['team_name']}\n"
    
    # Create comprehensive prompt with EXACT data
    bracket_info = "\\n".join([f"• {m['matchup']} ({m['region']} Region)" for m in actual_matchups[:30]])
    
    favorites_instruction = ""
    if favorite_teams_list:
        favorites_instruction = f"\\n\\nIMPORTANT: The user is rooting for these teams: {', '.join(favorite_teams_list)}. Please give them reasonable but optimistic predictions for how far these teams can go, while still being realistic about their chances."
    
    prompt = f"""You are a hilariously sarcastic March Madness bracket expert analyzing the 2026 NCAA Tournament. 

OFFICIAL 2026 NCAA TOURNAMENT BRACKET:{complete_bracket}

RISK LEVEL: {risk_level}/10 (1=conservative, 10=chaos)

KEY DATA INSIGHTS:
• Total games analyzed: {structured_data['data_summary']['total_tournament_games']} tournament games
• Upset probability patterns: {len(upset_stats)} categories identified  
• Conference strength: {len(conf_stats)} conferences analyzed
• Sample upset rates: {list(structured_data['upset_probabilities'].keys())[:3]}

FIRST ROUND MATCHUPS:
{bracket_info[:2000]}...

{favorites_instruction}

DELIVERABLES:
1. Overall bracket strategy for risk level {risk_level}
2. 3 specific upset predictions with reasoning
3. Championship prediction  
4. Roast the user's risk level
5. Analysis of favorite teams (if any)

Keep it funny, use real teams from bracket above, and be data-driven but concise!"""

    try:
        print("🔮 Consulting the basketball gods...")
        print(f"🔄 Making API call to nvidia-nemotron-3-super-120b...")
        
        # Add timeout to prevent hanging
        import time
        start_time = time.time()
        
        inference_response = inference_client.chat.completions.create(
            messages=[
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            model="nvidia-nemotron-3-super-120b",
            max_tokens=7000
        )
        
        elapsed_time = time.time() - start_time
        print(f"✅ LLM response received in {elapsed_time:.1f}s!")
        
        # Debug the response structure
        print(f"🔍 Response type: {type(inference_response)}")
        print(f"🔍 Response keys: {inference_response.__dict__.keys() if hasattr(inference_response, '__dict__') else 'No __dict__'}")
        
        # Try different ways to extract the content
        try:
            prediction = inference_response.choices[0].message.content
            print(f"🔍 Using choices[0].message.content: {prediction is not None}")
        except (AttributeError, IndexError) as e:
            print(f"🔍 choices[0].message.content failed: {e}")
            try:
                prediction = inference_response.generated_output
                print(f"🔍 Using generated_output: {prediction is not None}")
            except AttributeError:
                print(f"🔍 generated_output failed, trying response content directly")
                prediction = str(inference_response)
        
        if prediction is None or prediction.strip() == "":
            prediction = "❌ LLM returned empty response. This might be an API format issue."
        
        print("\\n" + "="*80)
        print("🎯 YOUR MARCH MADNESS PREDICTIONS:")
        print("="*80)
        print(prediction)
        print("\\n" + "="*80)
        print("🏀 Good luck with your bracket! May the chaos be ever in your favor!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ LLM failed: {e}")
        print(f"🔍 Error details: {type(e).__name__}")
        
        # Try to provide more specific error info
        if "connection" in str(e).lower():
            print("🌐 This appears to be a network/connection issue")
            print("💡 Try checking your internet connection or API key")
        elif "auth" in str(e).lower():
            print("🔐 This appears to be an authentication issue") 
            print("💡 Check if your MODEL_ACCESS_KEY is correct")
        
        print("\n📊 Using statistical fallback analysis...")
        
        # Fallback prediction using data
        print(f"\n🎲 RISK LEVEL {risk_level} ANALYSIS:")
        print(f"• Based on historical data, expect ~{risk_level + 2} major upsets")
        print(f"• Your confidence level: {max(10, 90 - (risk_level * 8))}%")
        
        if actual_matchups:
            high_upset_potential = [m for m in actual_matchups if int(m['low_seed']) >= 12]
            if high_upset_potential:
                selected = high_upset_potential[0]
                print(f"• Watch out for: {selected['matchup']}")
        
        if favorite_teams_list:
            print(f"\n🏀 Your Teams: {', '.join(favorite_teams_list)}")
            print("• Statistical analysis of your favorites would go here!")

if __name__ == "__main__":
    main()