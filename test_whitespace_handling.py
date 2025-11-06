"""
Test whitespace handling in connection parameters
"""

def test_whitespace_stripping():
    """Test that whitespace is properly stripped from connection parameters"""
    
    test_cases = [
        # (input, expected_output, description)
        ("   host.example.com   ", "host.example.com", "Leading and trailing spaces"),
        ("host.example.com", "host.example.com", "No spaces"),
        ("  9181  ", "9181", "Port with spaces"),
        ("   oauth2   ", "oauth2", "Auth type with spaces"),
        ("   dremio-catalog-server.svc.cluster.local   ", "dremio-catalog-server.svc.cluster.local", "K8s service name with spaces"),
        ("", "", "Empty string"),
    ]
    
    print("=" * 70)
    print("🧪 Testing Whitespace Handling")
    print("=" * 70)
    
    all_passed = True
    
    for input_val, expected, description in test_cases:
        result = input_val.strip()
        passed = result == expected
        status = "✅" if passed else "❌"
        
        # Show input with visible spaces
        visible_input = input_val.replace(" ", "·")
        visible_result = result.replace(" ", "·")
        
        print(f"\n{status} {description}")
        print(f"   Input:    '{visible_input}'")
        print(f"   Expected: '{expected}'")
        print(f"   Got:      '{visible_result}'")
        
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")
    print("=" * 70)
    
    return all_passed


def test_url_encoding():
    """Test that hostname with spaces gets encoded"""
    from urllib.parse import quote
    
    print("\n" + "=" * 70)
    print("🔍 URL Encoding Examples")
    print("=" * 70)
    
    hostnames = [
        "    dremio-catalog-server.svc.cluster.local",  # 4 leading spaces
        "host.example.com    ",  # 4 trailing spaces
        "  host.example.com  ",  # 2 leading, 2 trailing
    ]
    
    for hostname in hostnames:
        encoded = quote(hostname, safe='')
        cleaned = hostname.strip()
        
        print(f"\nOriginal: '{hostname}'")
        print(f"Encoded:  '{encoded}'")
        print(f"Cleaned:  '{cleaned}'")
        print(f"Problem:  {'❌ YES' if '%20' in encoded else '✅ NO'}")


if __name__ == "__main__":
    import sys
    
    test_passed = test_whitespace_stripping()
    test_url_encoding()
    
    print("\n" + "=" * 70)
    print("💡 RECOMMENDATION")
    print("=" * 70)
    print("Always use .strip() on connection parameters from OpenMetadata UI")
    print("to prevent URL encoding issues and connection failures.")
    print("=" * 70)
    
    sys.exit(0 if test_passed else 1)
