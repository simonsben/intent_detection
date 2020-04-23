from os import listdir
from re import compile, search
from utilities.data_management import make_path


file_regex = compile(r'\.py$')
files = listdir('.')
layer_base = make_path('execution/training/')

exclusions = [
    'train.py',
    'stacked.py',
    'calculate_thresholds.py',
    'deep_models.py'
]

# Train sub-layers
for file in files:
    if search(file_regex, file) is not None and file not in exclusions:
        print('Executing:', file)

        with open(layer_base / file) as fl:
            sub = exec(fl.read())

# Make predictions
predict_files = ['xg_boost.py', 'deep_model.py']
pred_base = make_path('execution/prediction')

for file in predict_files:
    with open(pred_base / file) as fl:
        exec(fl.read())

# Train stacked
with open(layer_base / 'stacked.py') as fl:
    exec(fl.read())

with open(layer_base / 'calculate_thresholds.py'):
    exec(fl.read())

print('\nAll models trained.')
