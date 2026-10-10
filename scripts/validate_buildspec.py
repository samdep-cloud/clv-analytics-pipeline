import yaml

with open("buildspec.yml") as f:
    config = yaml.safe_load(f)

expected = {"install", "build"}
actual = set(config["phases"])

assert expected <= actual, f"Missing phases: {expected - actual}"

print("Buildspec phases validated.")