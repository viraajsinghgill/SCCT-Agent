import sys, os, glob, importlib.util

def run_all_tests():
    print("=" * 70)
    print("  SCCT AGENT: AUTOMATED GOVERNANCE & METRIC TEST RUNNER")
    print("=" * 70)
    
    test_files = glob.glob("tests/test_*.py")
    total_tests = 0
    passed_tests = 0
    failed_tests = 0

    for tf in test_files:
        module_name = os.path.basename(tf).replace('.py', '')
        spec = importlib.util.spec_from_file_location(module_name, tf)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        
        test_funcs = [getattr(mod, f) for f in dir(mod) if f.startswith('test_') and callable(getattr(mod, f))]
        
        print(f"\n[SUITE] {module_name} ({len(test_funcs)} test cases):")
        for fn in test_funcs:
            total_tests += 1
            try:
                fn()
                print(f"  [PASS] {fn.__name__}")
                passed_tests += 1
            except Exception as e:
                print(f"  [FAIL] {fn.__name__}: {str(e)}")
                failed_tests += 1

    print("\n" + "=" * 70)
    print(f"  TEST SUMMARY: Total: {total_tests} | Passed: {passed_tests} | Failed: {failed_tests}")
    print("=" * 70)
    if failed_tests > 0:
        sys.exit(1)
    else:
        print("  ALL GOVERNANCE & RECONCILIATION TESTS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    run_all_tests()
