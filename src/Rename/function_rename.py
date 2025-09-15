import os

def rename_sequences(seq_file, rename_file, output_dir):
    try:
        with open(seq_file, 'r') as seq_f:
            sequences = seq_f.readlines()
        rename_dict = {}
        with open(rename_file, 'r') as rename_f:
            for line in rename_f:
                parts = line.strip().split("\t")
                if len(parts) == 2:
                    rename_dict[parts[0]] = parts[1]
        renamed_sequences = []
        for line in sequences:
            if line.startswith(">"):
                seq_name = line[1:].strip()  # Get the sequence name
                if seq_name in rename_dict:
                    new_name = rename_dict[seq_name]
                    renamed_sequences.append(f">{new_name}\n")
                else:
                    renamed_sequences.append(line)
            else:
                renamed_sequences.append(line) 
        input_filename = os.path.basename(seq_file)
        output_filename = f"Renamed_{input_filename}"
        output_file = os.path.join(output_dir, output_filename)
        with open(output_file, 'w') as output_f:
            output_f.writelines(renamed_sequences)

        return output_file
    except Exception as e:
        raise Exception(f"Error in renaming sequences: {str(e)}")