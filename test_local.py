#!/usr/bin/env python3
"""
Simple test script for SPF Study Coach
Tests basic functionality without requiring a database
"""

import sys
import os
import json

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    try:
        import json
        print("✅ json imported successfully")
    except ImportError as e:
        print(f"❌ json import failed: {e}")
        return False
    
    # These are optional for local testing - will be available on Vercel
    try:
        import flask
        print("✅ Flask imported successfully")
    except ImportError as e:
        print(f"⚠️  Flask not installed locally (will be available on Vercel): {e}")
    
    try:
        import psycopg2
        print("✅ psycopg2 imported successfully")
    except ImportError as e:
        print(f"⚠️  psycopg2 not installed locally (will be available on Vercel): {e}")
    
    return True

def test_seed_data():
    """Test that seed data files exist and are valid JSON"""
    seed_files = [
        'data/seeds/topics.json',
        'data/seeds/mcq.json',
        'data/seeds/saq.json',
        'data/seeds/flashcards.json'
    ]
    
    for seed_file in seed_files:
        try:
            with open(seed_file, 'r') as f:
                data = json.load(f)
                print(f"✅ {seed_file} loaded successfully ({len(data)} items)")
        except FileNotFoundError:
            print(f"❌ {seed_file} not found")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ {seed_file} invalid JSON: {e}")
            return False
    
    return True

def test_templates():
    """Test that all template files exist"""
    template_files = [
        'templates/base.html',
        'templates/index.html',
        'templates/drill_mcq.html',
        'templates/practice_saq.html',
        'templates/cheats.html',
        'templates/review.html'
    ]
    
    for template_file in template_files:
        if os.path.exists(template_file):
            print(f"✅ {template_file} exists")
        else:
            print(f"❌ {template_file} not found")
            return False
    
    return True

def test_static_files():
    """Test that static files exist"""
    static_files = [
        'static/style.css',
        'static/app.js',
        'static/sw.js'
    ]
    
    for static_file in static_files:
        if os.path.exists(static_file):
            print(f"✅ {static_file} exists")
        else:
            print(f"❌ {static_file} not found")
            return False
    
    return True

def test_config_files():
    """Test that configuration files exist"""
    config_files = [
        'vercel.json',
        'requirements.txt',
        'README.md'
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"✅ {config_file} exists")
        else:
            print(f"❌ {config_file} not found")
            return False
    
    return True

def main():
    """Run all tests"""
    print("🧪 Testing SPF Study Coach...")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("Seed Data Tests", test_seed_data),
        ("Template Tests", test_templates),
        ("Static File Tests", test_static_files),
        ("Config File Tests", test_config_files)
    ]
    
    all_passed = True
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        if not test_func():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! The application is ready for deployment.")
        print("\nTo run locally:")
        print("1. Set up environment variables")
        print("2. Run: python api/index.py")
        print("\nTo deploy to Vercel:")
        print("1. Run: ./deploy.sh")
        print("2. Set up Vercel Postgres database")
        print("3. Add environment variables in Vercel dashboard")
    else:
        print("❌ Some tests failed. Please fix the issues before deploying.")
        sys.exit(1)

if __name__ == "__main__":
    main()
