"""
Test script for relevance filtering and scoring.

Validates that the relevance filtering and scoring correctly identifies and weights articles.
"""
from config.relevance_filter import is_article_relevant_to_ticker, compute_relevance_score


def test_relevance_filtering():
    """Test relevance filtering with example articles."""
    
    # Test cases: (article_dict, symbol, expected_relevant, description)
    test_cases = [
        # Clearly relevant articles
        (
            {
                "headline": "Apple stock jumps after strong iPhone 16 sales beat Wall Street expectations",
                "raw_text": "Apple Inc. reported better-than-expected iPhone sales, sending AAPL shares higher."
            },
            "AAPL",
            True,
            "Relevant: Apple-specific news with ticker mention"
        ),
        (
            {
                "headline": "Microsoft Azure revenue grows 40% in Q4, MSFT shares rise",
                "raw_text": "Microsoft Corporation announced strong cloud revenue growth."
            },
            "MSFT",
            True,
            "Relevant: Microsoft-specific news"
        ),
        (
            {
                "headline": "Tesla (TSLA) announces new Model 3 production milestone",
                "raw_text": "Tesla Inc. reached a new production milestone for its Model 3."
            },
            "TSLA",
            True,
            "Relevant: Tesla news with ticker in parentheses"
        ),
        
        # Clearly irrelevant articles (noise)
        (
            {
                "headline": "Astrocytoma Market Research and Forecast Report 2025–2035: Sanofi, Sun Pharma, Eli Lilly...",
                "raw_text": "The global astrocytoma market is expected to grow significantly from 2025 to 2035."
            },
            "AAPL",
            False,
            "Irrelevant: Generic market research report"
        ),
        (
            {
                "headline": "INVESTOR ALERT: Pomerantz Law Firm Reminds Investors With Losses on Their Investment in Freeport-McMoRan Inc. of Class Action Lawsuit",
                "raw_text": "Investors who purchased shares of Freeport-McMoRan may be eligible for compensation."
            },
            "MSFT",
            False,
            "Irrelevant: Law firm investor alert"
        ),
        (
            {
                "headline": "MaintainX Ranked Number 82 Fastest-Growing Company in North America on the 2025 Deloitte Technology Fast 500",
                "raw_text": "MaintainX has been recognized as one of the fastest-growing companies."
            },
            "TSLA",
            False,
            "Irrelevant: Generic ranking announcement"
        ),
        (
            {
                "headline": "Donald Trump claims Saudi crown prince 'knew nothing' about murder of journalist Jamal Khashoggi",
                "raw_text": "Political news about Saudi Arabia and journalist murder."
            },
            "AAPL",
            False,
            "Irrelevant: Political/geopolitical news unrelated to company"
        ),
        (
            {
                "headline": "The Biotech Sector is Seeing a Major Boost From Programmable Cell Therapies in Chronic Disease Care",
                "raw_text": "Industry-wide analysis of biotech sector trends."
            },
            "JNJ",
            False,
            "Irrelevant: Generic sector analysis, not company-specific"
        ),
        
        # Edge cases
        (
            {
                "headline": "Apple Inc. announces new product line",
                "raw_text": "Apple Inc. has announced a new product line that will be available next year."
            },
            "AAPL",
            True,
            "Relevant: Company name match"
        ),
        (
            {
                "headline": "Tech stocks rally as Apple and Microsoft report earnings",
                "raw_text": "The technology sector saw gains as Apple and Microsoft both reported strong earnings."
            },
            "AAPL",
            True,
            "Relevant: Multi-company news but Apple is mentioned"
        ),
        
        # Scoring examples
        (
            {
                "headline": "Apple Inc stock surges on strong earnings report",
                "raw_text": "Apple Inc. reported record earnings, sending AAPL stock higher."
            },
            "AAPL",
            True,
            "High score: Company name + finance terms (should score ~1.0)"
        ),
        (
            {
                "headline": "New iPhone 15 features revealed",
                "raw_text": "Apple unveiled new features for the iPhone 15."
            },
            "AAPL",
            True,
            "Lower score: Product name only (should score ~0.3-0.4)"
        ),
        (
            {
                "headline": "AAPL shares rise after analyst upgrade",
                "raw_text": "Analysts upgraded AAPL stock price target."
            },
            "AAPL",
            True,
            "High score: Ticker + finance terms (should score ~0.8)"
        ),
    ]
    
    print("Testing relevance filtering and scoring...")
    print("=" * 80)
    print("\nScoring scale:")
    print("  1.0 = Company name + finance terms (e.g., 'Apple Inc stock')")
    print("  0.8 = Ticker + finance terms (e.g., 'AAPL stock')")
    print("  0.7 = Company name alone (e.g., 'Apple Inc')")
    print("  0.6 = Ticker alone (e.g., 'AAPL')")
    print("  0.4 = Product + finance terms (e.g., 'iPhone stock')")
    print("  0.3 = Product alone (e.g., 'iPhone') - minimum threshold")
    print("  0.0 = Not relevant or noise")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for article_dict, symbol, expected_relevant, description in test_cases:
        is_relevant, score = compute_relevance_score(article_dict, symbol)
        status = "✓ PASS" if is_relevant == expected_relevant else "✗ FAIL"
        
        if is_relevant == expected_relevant:
            passed += 1
        else:
            failed += 1
        
        print(f"\n{status}: {description}")
        print(f"  Symbol: {symbol}")
        print(f"  Headline: {article_dict['headline'][:70]}...")
        print(f"  Expected relevant: {expected_relevant}, Got: {is_relevant}, Score: {score:.2f}")
        
        if is_relevant != expected_relevant:
            print(f"  ⚠️  MISMATCH!")
    
    print("\n" + "=" * 80)
    print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    
    if failed == 0:
        print("✅ All tests passed!")
        return True
    else:
        print(f"❌ {failed} test(s) failed")
        return False


if __name__ == "__main__":
    test_relevance_filtering()

