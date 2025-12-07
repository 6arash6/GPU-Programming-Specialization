import os
import re
import sys
import pickle
import base64

OUTPUT_FILE_KEY = "output_file"
VALIDATION_STEPS_KEY = "validation_steps"
FILE_VALIDATION_KEY = "file_validation"
VALIDATION_TYPE_KEY = "validation_type"
VALIDATION_OBJ_KEY = "validation_obj"
PART_ID_NUM_THREADS_MAP_KEY = "part_id_num_threads_map"
REGEX_KEY = "regex"
VALID_KEY = "valid"
INVALID_KEY = "invalid"
LIST_VALIDATION_TYPE_KEY = "list"
RECURRING_VALIDATION_TYPE_KEY = "recurring"
RECURRING_PAIR_VALIDATION_TYPE_KEY = "recurring_pair"
MULTIPLE_THREAD_VALIDATION_TYPE_KEY = "multiple_threads"
FILE_THREAD_MAP_TYPE_KEY = "file_thread_map"
DRIVER_API_KEY = "driver_api"
RUNTIME_API_KEY = "runtime_api"
DATA_SEARCH_KEY = "data_search"
CPU_GPU_MEMORY_KEY = "cpu_gpu_memory"
CPU_GPU_MEMORY_MATH_KEY = "cpu_gpu_memory_math"
MULTI_CPU_INPUT_KEY = "multi_cpu_input"
MULTI_CPU_OUTPUT_KEY = "multi_cpu_output"
STEPS_KEY = "steps"
PART_IDS_FILENAME_MAP_KEY = "part_ids_filename_map"
RECURRING_VALIDATION_NUM_ITERATIONS_KEY = "num_iterations"
RESULTS_FILE_NAME = "results.txt"
OUTPUT_FILE_NAME = "output.txt"
UNLIMITED_PAIRS = "unlimited"

OUTPUT_START_THREAD_SUFFIX = "started"
OUTPUT_COMPLETED_THREAD_SUFFIX = "completed"
MULTIPLE_CPP_PREFIX = "C++11: "
ALL_THREADS_STARTED_LINE = "Signaling threads to do work."
ALL_THREADS_COMPLETE_LINE = "All threads completed."

ENCODED_FILE_LOCATION = "regex.b64"

class Validator():
    regexs = None

    def create_validation_step_string(self, validation_step: list, valid: bool, file_location: str) -> str:
        if valid:
            output_str_suffix = "was found."
            output_str_base = validation_step[VALID_KEY]
        else:
            output_str_suffix = "was not found."
            output_str_base = validation_step[INVALID_KEY]
        return f"{output_str_base} {file_location} {output_str_suffix}"


    def create_file_validation_string(self, file_validation_str_obj: list, file_location: str, valid: bool) -> str:
        if valid:
            file_validation_list = file_validation_str_obj[VALID_KEY]
        else:
            file_validation_list = file_validation_str_obj[INVALID_KEY]
        file_validation_list.insert(1, file_location)
        return " ".join(file_validation_list)


    def use_regex_on_file(self, file_location:str, regex_string:str) -> int:
        total_num_iterations = 0
        try:
            with open(file_location) as fo:
                line = fo.readline()
                # Loop until EOF
                while line != '':
                    if re.search(regex_string, line):
                        total_num_iterations += 1
                    # Read next line
                    line = fo.readline()
        except Exception as e:
            print(f"INVALID: An exception occured while attempting to read file {file_location}, it follows: {e}")
        return total_num_iterations


    def validate_recurring_pairs_file(self, regex_obj: any) -> bool:
        valid = False
        comparison_datasets = 0
        filename = regex_obj[OUTPUT_FILE_KEY]
        file_location = os.path.join(os.getcwd(),filename)
        validation_steps = regex_obj[VALIDATION_STEPS_KEY]
        part_a_step = validation_steps[0]
        regex_str = part_a_step[REGEX_KEY]
        num_part_a_datasets = self.use_regex_on_file(file_location=file_location, regex_string=regex_str)
        part_b_step = validation_steps[1]
        regex_str = part_b_step[REGEX_KEY]
        num_part_b_datasets = self.use_regex_on_file(file_location=file_location, regex_string=regex_str)
        comparison_datasets = num_part_a_datasets - num_part_b_datasets
        if comparison_datasets == 0:
            valid = True
        print(self.create_file_validation_string(file_validation_str_obj=regex_obj[FILE_VALIDATION_KEY], 
                                            file_location=file_location, valid=valid))
        return valid


    def validate_file(self, regex_obj: any, validation_type: str) -> bool:
        filename = regex_obj[OUTPUT_FILE_KEY]
        file_location = os.path.join(os.getcwd(),filename)
        valid = True
        validation_steps = regex_obj[VALIDATION_STEPS_KEY]
        for validation_step in validation_steps:
            regex_str = validation_step[REGEX_KEY]
            temp_valid = self.validation_test(validation_step=validation_step, file_location=file_location,
                                        validation_type=validation_type, regex_str=regex_str)
            print(self.create_validation_step_string(validation_step=validation_step,valid=temp_valid, file_location=file_location))
            valid = valid and temp_valid
        print(self.create_file_validation_string(file_validation_str_obj=regex_obj[FILE_VALIDATION_KEY], 
                                            file_location=file_location, valid=valid))
        return valid


    def validation_test(self, validation_step: any, file_location:str, validation_type: str, regex_str: str) -> bool:
        valid = False
        total_num_iterations = self.use_regex_on_file(file_location=file_location, regex_string=regex_str)
        if validation_type == LIST_VALIDATION_TYPE_KEY or validation_type == FILE_THREAD_MAP_TYPE_KEY:
            valid = total_num_iterations > 0
        elif validation_type == RECURRING_VALIDATION_TYPE_KEY:
            required_num_iterations = validation_step[RECURRING_VALIDATION_NUM_ITERATIONS_KEY]
            valid = total_num_iterations >= required_num_iterations
        return valid


    def validate_file_thread_map(self, regex_obj: any) -> bool:
        validation_steps = regex_obj[VALIDATION_STEPS_KEY]
        valid = True
        for validation_api_key, validation_api_obj in validation_steps.items():
            part_ids_filename_map = validation_api_obj[PART_IDS_FILENAME_MAP_KEY]
            validation_obj = validation_api_obj[VALIDATION_OBJ_KEY]
            for part_id, filename in part_ids_filename_map.items():
                validation_obj[OUTPUT_FILE_KEY] = filename
                print(f"Validating {validation_api_key} part_id: {part_id}, filename: {filename} :")
                valid = self.validate_file(regex_obj=validation_obj, validation_type=FILE_THREAD_MAP_TYPE_KEY) and valid
        return valid


    def validate_multithreaded_output_str(self, output_string, suffix):
        thread_idx = -1
        if output_string.find(suffix) > -1:
            try:
                thread_indexes = re.findall(r'\d+', output_string)
                if len(thread_indexes) > 0:
                    thread_idx = int(thread_indexes[0])
                    print(f"VALID: Found thread index: {thread_idx} in line: '{output_string}'")
                    valid = True
                else:
                    print(f"INVALID: The following line was supposed to contain the {suffix}: '{output_string}'")
            except:
                print(f"INVALID: An error has occurred during parsing the following line for thread id: '{output_string}'")
        else:
            print(f"INVALID: The following line was supposed to contain the {suffix}: '{output_string}'")


    def validate_multithreaded_file(self, key: str, filename: str, part_id, num_threads: int) -> bool:
        file_loc = os.path.join(os.getcwd(),filename)
        with open(file_loc, "r") as fo:
            line = fo.readline().rstrip().replace(MULTIPLE_CPP_PREFIX, "",1)
            print(f"{part_id} should have {num_threads} started and completed with the output of each stage (start, complete) output to a file called {filename} in {os.getcwd()}.")
            # Loop until EOF
            while line != '':
                found = False
                print(f"Validating line: {line}")
                if key == "multiple_cpp":
                    if ALL_THREADS_STARTED_LINE in line:
                        found = True
                        print(f"VALID: The current line indicates that all threads have been started, which is a good sign.")
                    elif ALL_THREADS_COMPLETE_LINE in line:
                        found = True
                        print(
        """VALID: The current line indicates that all threads have completed their work, which is a good sign.
        No further output lines will be processed.  If a thread did not complete its work until after this line, 
        then you will not recieve full grades""")
                if not found:
                    if OUTPUT_START_THREAD_SUFFIX in line:
                        self.validate_multithreaded_output_str(line, OUTPUT_START_THREAD_SUFFIX)
                    elif OUTPUT_COMPLETED_THREAD_SUFFIX in line:
                        self.validate_multithreaded_output_str(line, OUTPUT_COMPLETED_THREAD_SUFFIX)
                    else:
                        print(f"INVALID: The following line of output is extraneous and should not be included: '{line}'")
                # Read next line
                line = fo.readline().rstrip().replace(MULTIPLE_CPP_PREFIX, "",1)
        print(
    """Please pay attention to any output that starts with INVALID, as this will help identify any issues with the output of your code.
    If there are no lines with invalid and only lines that start with VALID for the start and completion each thread, then you should submit this assignment as your output is valid.
    This does not guarantee that the appropriate number of threads were started and completed for the current assignment part.
    Note: This validator only checks if certain patterns exist, if your output doesn't include for example the start line for a thread but includes the complete line, no errors will be displayed."""
    )


    def perform_validation_multithreaded(self, key: str, regex_obj: any) -> bool:
        part_id_num_threads_map = regex_obj[PART_ID_NUM_THREADS_MAP_KEY]
        for part_id, num_threads in part_id_num_threads_map.items():
            filename = f"output-{part_id}.txt"
            self.validate_multithreaded_file(key=key, part_id=part_id, filename=filename, num_threads=num_threads)


    def encode_regexs_to_file(self):
        regexs_pickle_str = pickle.dumps(self.regexs)
        encoded_bytes = base64.b64encode(regexs_pickle_str)
        file_location = os.path.join(os.getcwd(),ENCODED_FILE_LOCATION)
        try:
            with open(file_location, 'wb') as fo:
                fo.write(encoded_bytes)
        except Exception as e:
            print(f"exception: {e}")


    def decode_file_to_regexs(self):
        file_location = os.path.join(os.getcwd(),ENCODED_FILE_LOCATION)
        try:
            with open(file_location, 'rb') as fo:
                line = fo.readline()
                regexs_pickle_str = base64.b64decode(line)
                self.regexs = pickle.loads(regexs_pickle_str)
        except Exception as e:
            print(f"exception: {e}")


if __name__ == '__main__':
    key = None
    validator = Validator()
    if os.path.exists(os.path.join(os.getcwd(),ENCODED_FILE_LOCATION)):
        validator.decode_file_to_regexs()
    if len(sys.argv) > 1 and validator.regexs:
        key = sys.argv[1]
        regex_obj = validator.regexs[key]
        validation_type = regex_obj[VALIDATION_TYPE_KEY]
        if validation_type == MULTIPLE_THREAD_VALIDATION_TYPE_KEY:
            validator.perform_validation_multithreaded(key=key, regex_obj=regex_obj)
        elif validation_type == FILE_THREAD_MAP_TYPE_KEY:
            validator.validate_file_thread_map(regex_obj=regex_obj)
        elif validation_type == RECURRING_PAIR_VALIDATION_TYPE_KEY:
            validator.validate_recurring_pairs_file(regex_obj=regex_obj)
        else:
            validator.validate_file(regex_obj=regex_obj, validation_type=validation_type)
    else:
        print(f"A required validation key was not passed to the validation script.")