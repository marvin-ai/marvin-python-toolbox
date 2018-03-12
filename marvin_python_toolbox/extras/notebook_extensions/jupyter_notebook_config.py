#!/usr/bin/env python
# coding=utf-8

# Copyright [2017] [B2W Digital]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


def marvin_code_export(model, **kwargs):

    import autopep8
    import inspect
    import re
    from marvin_python_toolbox.common.config import Config

    print("Executing the marvin export hook script...")

    if model['type'] != 'notebook':
        return

    # import ipdb; ipdb.set_trace()

    cells = model['content']['cells']

    artifacts = {
        'marvin_initial_dataset': re.compile(r"(\bmarvin_initial_dataset\b)"),
        'marvin_dataset': re.compile(r"(\bmarvin_dataset\b)"),
        'marvin_model': re.compile(r"(\bmarvin_model\b)"),
        'marvin_metrics': re.compile(r"(\bmarvin_metrics\b)")
    }

    batch_exec_pattern = re.compile("(def\s+execute\s*\(\s*self\s*,\s*params\s*,\s*\*\*kwargs\s*\)\s*:)")
    online_exec_pattern = re.compile("(def\s+execute\s*\(\s*self\s*,\s*input_message\s*,\s*params\s*,\s*\*\*kwargs\s*\)\s*:)")

    CLAZZES = {
        "acquisitor": "AcquisitorAndCleaner",
        "tpreparator": "TrainingPreparator",
        "trainer": "Trainer",
        "evaluator": "MetricsEvaluator",
        "ppreparator": "PredictionPreparator",
        "predictor": "Predictor",
        "feedback": "Feedback"
    }

    for cell in cells:
        if cell['cell_type'] == 'code' and cell["metadata"].get("marvin_cell", False):
            source = cell["source"]
            new_source = autopep8.fix_code(source, options={'max_line_length': 160})

            marvin_action = cell["metadata"]["marvin_cell"]
            marvin_action_clazz = getattr(__import__(Config.get("package")), CLAZZES[marvin_action])
            source_path = inspect.getsourcefile(marvin_action_clazz)

            fnew_source_lines = []
            for new_line in new_source.split("\n"):
                fnew_line = "        " + new_line + "\n" if new_line.strip() else "\n"

                if not new_line.startswith("import") and not new_line.startswith("from") and not new_line.startswith("print"):
                    for artifact in artifacts.keys():
                        fnew_line = re.sub(artifacts[artifact], 'self.' + artifact, fnew_line)

                fnew_source_lines.append(fnew_line)

            if marvin_action == "predictor":
                fnew_source_lines.append("        return final_prediction\n")
                exec_pattern = online_exec_pattern

            elif marvin_action == "ppreparator":
                fnew_source_lines.append("        return input_message\n")
                exec_pattern = online_exec_pattern

            elif marvin_action == "feedback":
                fnew_source_lines.append("        return \"Thanks for the feedback!\"\n")
                exec_pattern = online_exec_pattern

            else:
                exec_pattern = batch_exec_pattern

            fnew_source = "".join(fnew_source_lines)

            with open(source_path, 'r+') as fp:
                lines = fp.readlines()
                fp.seek(0)
                for line in lines:
                    if re.findall(exec_pattern, line):
                        fp.write(line)
                        fp.write(fnew_source)
                        fp.truncate()

                        break
                    else:
                        fp.write(line)

            print ("File {} updated!".format(source_path))

    print("Finished the marvin export hook script...")


c.FileContentsManager.pre_save_hook = marvin_code_export
