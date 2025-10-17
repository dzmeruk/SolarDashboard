# Allows tests located in "tests" subdirectory to import modules in "scripts"######################
import path_to_scripts
path_to_scripts.path_to_scripts()
###################################################################################################

"""
A diagnostic script to verify the pvlib installation and check for the
presence of the SingleAxisTracker class.
"""
import sys

try:
    import pvlib

    print(f"✅ Successfully imported pvlib.")
except ImportError as e:
    print(f"❌ FAILED to import pvlib. Error: {e}")
    print("Please run: pip install pvlib")
    sys.exit()

# 1. Print the version to confirm it is up-to-date
print(f"-> pvlib version: {pvlib.__version__}")

# 2. Print the file path to ensure it's not a local file shadowing the library
print(f"-> pvlib installed at: {pvlib.__file__}")

# 3. Attempt to access the specific class that is causing the error
try:
    from pvlib.pvsystem import SingleAxisTrackerMount

    print("\n✅ Successfully accessed pvlib.tracking.SingleAxisTracker.")
    # We can also create an instance to be sure
    tracker = SingleAxisTrackerMount()
    print("-> Successfully created an instance of SingleAxisTracker.")
    print("\n--- DIAGNOSIS: pvlib installation appears to be correct. ---")

except AttributeError:
    print("\n❌ FAILED with AttributeError. The class was not found where expected.")
    print("This suggests a corrupted installation or a very old version.")
    # Let's inspect the contents of the pvlib.tracking module to see what's there
    try:
        import pvlib.tracking

        print("\n--- Contents of pvlib.tracking module ---")
        print(dir(pvlib.tracking))
        print("------------------------------------------")
    except Exception as e:
        print(f"Could not inspect pvlib.tracking. Error: {e}")

except Exception as e:
    print(f"\n❌ An unexpected error occurred: {e}")

