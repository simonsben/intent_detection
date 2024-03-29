from pathlib import Path
from keras import backend
from tensorflow.compat.v1 import global_variables
from tensorflow.compat.v1.graph_util import convert_variables_to_constants


def load_model_weights(model, weights_path):
    """ Loads tensorflow model weights """
    weights_path = Path(weights_path)
    if not weights_path.exists():
        raise FileNotFoundError('Specified weights file does not exist.')

    model.load_weights(str(weights_path), by_name=True)


def freeze_session(model, clear_devices=True):
    """
    Freezes the state of a session into a pruned computation graph.
    Modified version of: https://stackoverflow.com/questions/45466020/how-to-export-keras-h5-to-tensorflow-pb

    Creates a new computation graph where variable nodes are replaced by
    constants taking their current value in the session. The new graph will be
    pruned so subgraphs that are not necessary to compute the requested
    outputs are removed.
    :param model: Keras model to be frozen.
    :param list clear_devices: Remove the device directives from the graph for better portability.
    :return: The frozen graph definition.
    """
    session = backend.get_session()
    graph = session.graph

    with graph.as_default():
        variables_to_freeze = list(set(variable.op.name for variable in global_variables()))

        output_names = [output.op.name for output in model.outputs]
        output_names += [variable.op.name for variable in global_variables()]

        input_graph_def = graph.as_graph_def()

        # Clear device-specific instructions
        if clear_devices:
            for node in input_graph_def.node:
                node.device = ""

        return convert_variables_to_constants(session, input_graph_def, output_names, variables_to_freeze)



