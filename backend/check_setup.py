"""
Quick script to check if backend is set up correctly.
"""
import os
from pathlib import Path

print("=" * 60)
print("Backend Setup Check")
print("=" * 60)

# Check .env file
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    print("\n[OK] .env file exists")
    
    # Check environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    alphavantage_key = os.getenv("ALPHAVANTAGE_API_KEY")
    
    print(f"\nEnvironment Variables:")
    print(f"  SUPABASE_URL: {'[OK] SET' if supabase_url else '[ERROR] NOT SET'}")
    print(f"  SUPABASE_KEY: {'[OK] SET' if supabase_key else '[ERROR] NOT SET'}")
    print(f"  OPENAI_API_KEY: {'[OK] SET' if openai_key else '[WARN] OPTIONAL (for sentiment enrichment)'}")
    print(f"  ALPHAVANTAGE_API_KEY: {'[OK] SET' if alphavantage_key else '[ERROR] NOT SET (required for news)'}")
    
    if not supabase_url or not supabase_key:
        print("\n[ERROR] Missing required Supabase credentials!")
        print("   Add SUPABASE_URL and SUPABASE_KEY to .env file")
    
    if not openai_key:
        print("\n[WARN] Missing OpenAI API key (needed for sentiment analysis)")
        print("   Add OPENAI_API_KEY to .env file")
    
else:
    print("\n[ERROR] .env file NOT found!")
    print("\nCreate a .env file in the backend/ folder with:")
    print("  SUPABASE_URL=https://your-project.supabase.co")
    print("  SUPABASE_KEY=your-anon-key")
    print("  ALPHAVANTAGE_API_KEY=your-alpha-vantage-key")
    print("  OPENAI_API_KEY=sk-your-key (optional - for sentiment enrichment)")

# Check uvicorn
try:
    import uvicorn
    print(f"\n[OK] Uvicorn installed (version {uvicorn.__version__})")
    print("   Run server with: python -m uvicorn app:app --reload")
except ImportError:
    print("\n[ERROR] Uvicorn not installed!")
    print("   Run: pip install uvicorn[standard]")

# Check other dependencies
deps = ["fastapi", "supabase", "openai", "pandas", "sklearn"]
missing = []
for dep in deps:
    try:
        __import__(dep)
        print(f"[OK] {dep} installed")
    except ImportError:
        print(f"[ERROR] {dep} NOT installed")
        missing.append(dep)

if missing:
    print(f"\n[WARN] Missing dependencies: {', '.join(missing)}")
    print("   Run: pip install -r requirements.txt")

print("\n" + "=" * 60)
print("Setup Check Complete!")
print("=" * 60)

