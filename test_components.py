"""
BioSync Tele-Rescue - Test Suite
Basic tests for the healthcare dashboard components
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all components can be imported"""
    try:
        from components.data_manager import data_manager
        from components.ui_components import ui
        from components.pages import LandingPage, PatientDashboard, DoctorDashboard
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_data_manager():
    """Test data manager functionality"""
    try:
        from components.data_manager import data_manager

        # Test dashboard metrics
        metrics = data_manager.get_dashboard_metrics()
        assert isinstance(metrics, dict)
        assert 'total_consultations' in metrics
        print("✅ Data manager metrics test passed")

        # Test vitals data
        vitals = data_manager.get_vitals_data()
        assert isinstance(vitals, dict)
        assert 'Heart Rate' in vitals
        print("✅ Data manager vitals test passed")

        # Test feedback pipeline
        before_count = len(data_manager.get_feedback_entries())
        data_manager.submit_feedback(
            patient="Test Patient",
            doctor="Dr. Sarah Johnson",
            consultation_type="Consultation",
            rating=5,
            communication=5,
            wait_time=4,
            recommend=True,
            comments="Automated test feedback entry",
        )
        after_count = len(data_manager.get_feedback_entries())
        assert after_count == before_count + 1

        summary = data_manager.get_feedback_summary()
        assert isinstance(summary, dict)
        assert 'avg_rating' in summary

        trends = data_manager.get_feedback_trends(days=7)
        assert not trends.empty
        assert 'Avg Rating' in trends.columns
        print("✅ Data manager feedback pipeline test passed")

        return True
    except Exception as e:
        print(f"❌ Data manager test failed: {e}")
        return False

def test_ui_components():
    """Test UI components"""
    try:
        from components.ui_components import ui
        # Test that UI class exists and has methods
        assert hasattr(ui, 'inject_global_css')
        assert hasattr(ui, 'create_metric_card')
        print("✅ UI components test passed")
        return True
    except Exception as e:
        print(f"❌ UI components test failed: {e}")
        return False

def run_tests():
    """Run all tests"""
    print("🧪 Running BioSync Tele-Rescue Tests")
    print("=" * 40)

    tests = [
        test_imports,
        test_data_manager,
        test_ui_components
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print("=" * 40)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️ Some tests failed")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)