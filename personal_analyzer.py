#!/usr/bin/env python3
"""
Easy interface for setting your favorite teams and getting personalized March Madness analysis
"""

from backend.data_analyzer import MarchMadnessAnalyzer

def analyze_my_teams(team1, team2, team3, risk_level=5):
    """
    Simple function to analyze YOUR favorite teams
    
    Example:
        analyze_my_teams("Duke", "North Carolina", "Virginia", risk_level=7)
    
    Args:
        team1, team2, team3: Names of your favorite teams
        risk_level: How risky your bracket should be (1=safe, 10=chaos)
    """
    print("🏀 ANALYZING YOUR FAVORITE TEAMS")
    print("=" * 40)
    
    # Create analyzer
    analyzer = MarchMadnessAnalyzer()
    
    # Set your preferences
    print(f"\n🎯 Your Teams: {team1}, {team2}, {team3}")
    print(f"🎲 Risk Level: {risk_level}/10")
    
    result = analyzer.set_user_preferences([team1, team2, team3], risk_level)
    
    if result.get('success'):
        # Get personalized analysis
        analysis = analyzer.get_personalized_analysis()
        
        if 'error' not in analysis:
            print("\n" + "="*40)
            print("📊 YOUR TEAMS IN 2026 TOURNAMENT:")
            print("="*40)
            
            for team_name, team_analysis in analysis['user_teams_analysis'].items():
                if '2026_seed' in team_analysis:
                    seed = team_analysis['2026_seed']
                    recommendation = team_analysis['recommendation']
                    path = team_analysis.get('tournament_path', {})
                    
                    print(f"\n🏀 {team_name.upper()}")
                    print(f"   Seed: {seed}")
                    print(f"   {recommendation}")
                    
                    if 'first_round_opponent' in path and path['first_round_opponent']:
                        print(f"   First opponent: {path['first_round_opponent']}")
                    if 'championship_odds' in path:
                        print(f"   Outlook: {path['championship_odds']}")
                else:
                    status = team_analysis.get('tournament_status', 'Not in tournament')
                    print(f"\n💔 {team_name.upper()}: {status}")
            
            # Tournament outlook
            outlook = analysis['tournament_outlook']
            print(f"\n" + "="*40)
            print("🎯 YOUR TOURNAMENT STRATEGY:")
            print("="*40)
            print(f"📈 {outlook['your_teams_summary']}")
            print(f"🎲 {outlook['bracket_strategy']}")
            
        else:
            print(f"\n❌ Analysis Error: {analysis['error']}")
    else:
        print(f"\n❌ Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    # Example usage - CHANGE THESE TO YOUR TEAMS!
    print("💡 EXAMPLE: Analyzing Duke, Kentucky, and Villanova with medium risk")
    analyze_my_teams("Duke", "Kentucky", "Villanova", risk_level=6)
    
    print("\n\n" + "="*60)
    print("TO USE WITH YOUR TEAMS:")
    print("="*60)
    print("from personal_analyzer import analyze_my_teams")
    print("")
    print("# Change these to YOUR favorite teams:")
    print('analyze_my_teams("Your Team 1", "Your Team 2", "Your Team 3", risk_level=7)')
    print("")
    print("Risk levels: 1=Very Safe, 5=Balanced, 10=Pure Chaos")