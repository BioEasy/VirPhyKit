def wrtcfg(*migr):
    """Generate matrix content as a string instead of writing to file."""
    tlen = len(migr)
    str0 = ['0'] * tlen
    output = []
    for ii in range(0, tlen):
        for jj in range(0, tlen):
            if ii == jj: continue
            str1 = str0[:]
            str1[jj:jj + 1] = '%d' % 1
            output.append('<parameter id="%2s-to-%2s" value="\n' % (migr[ii], migr[jj]))
            for kk in range(0, ii):
                output.append(' '.join(str0) + '\n')
            output.append(' '.join(str1) + '\n')
            for kk in range(ii + 1, tlen):
                output.append(' '.join(str0) + '\n')
            output.append('"/>\n')
    return ''.join(output)

def wrt_rewards(*migr):
    """Generate rewards content as a string for the given traits."""
    tlen = len(migr)
    output = ['<rewards>\n']
    for ii in range(0, tlen):
        values = ['0.0'] * tlen
        values[ii] = '1.0'
        output.append(f'    <parameter id="{migr[ii]}_reward" value="{" ".join(values)}" />\n')
    output.append('</rewards>\n')
    return ''.join(output)

def process_xml(input_xml_path, migr, output_xml_path):
    """Read XML, insert matrix and rewards before the specified comment, and save to new XML."""
    try:
        with open(input_xml_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        with open('debug_log.txt', 'w', encoding='utf-8') as log:
            log.write('XML Lines:\n' + ''.join(lines))
        target_comment_patterns = [
            "<!--  END Ancestral state reconstruction",
            "<!-- END Ancestral state reconstruction",
            "</markovJumpsTreeLikelihood>"
        ]
        comment_index = -1
        for i, line in enumerate(lines):
            for pattern in target_comment_patterns:
                if pattern in line:
                    comment_index = i
                    break
            if comment_index != -1:
                break

        if comment_index == -1:
            return False, 'Error: Target markers "END Ancestral state reconstruction" or "</markovJumpsTreeLikelihood>" not found in XML file'
        matrix_content = wrtcfg(*migr)
        rewards_content = wrt_rewards(*migr)
        output_lines = lines[:comment_index] + [matrix_content, rewards_content] + lines[comment_index:]
        with open(output_xml_path, 'w', encoding='utf-8') as f:
            f.writelines(output_lines)
        return True, f'Success: Modified XML with matrix and rewards saved to {output_xml_path}'
    except UnicodeDecodeError:
        return False, 'Error: XML file encoding is not UTF-8'
    except Exception as e:
        return False, f'Error: {str(e)}'

def generate_config(migr_text, file_path, filename, input_xml_path=None):
    """Generate config file or process XML based on input_xml_path."""
    if not migr_text:
        return False, 'Error: No migr parameters provided'
    if not file_path:
        return False, 'Error: No save directory provided'
    if not filename:
        return False, 'Error: No filename provided'
    try:
        if ',' not in migr_text and len(migr_text.strip().split()) > 1:
            return False, 'Error: The Migr Parameters input is incorrect. Please check. Please separate different parameters with English commas.'

        migr = [x.strip() for x in migr_text.split(',') if x.strip()]
        if not migr or len(migr) < 2:
            return False, 'Error: No valid migr parameters provided or fewer than 2 parameters'
        if input_xml_path:
            output_file = file_path.rstrip('/\\') + '/' + filename
            if not output_file.endswith('.xml'):
                output_file += '.xml'
            return process_xml(input_xml_path, migr, output_file)
        else:
            output_file = file_path.rstrip('/\\') + '/' + filename
            if not output_file.endswith('.txt'):
                output_file += '.txt'
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(wrtcfg(*migr))
                f.write(wrt_rewards(*migr))  # Append rewards to txt output as well
            return True, f'Success: File with matrix and rewards saved to {output_file}'
    except Exception as e:
        return False, f'Error: {str(e)}'