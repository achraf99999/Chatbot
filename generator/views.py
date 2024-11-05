from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import json
import pandas as pd
import openpyxl
from django.http import JsonResponse
import sentencepiece

# Load the first model and tokenizer (improved error handling)
# Setup device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load the first model and tokenizer

model1_tokenizer = AutoTokenizer.from_pretrained("/code_generator/distilroberta_marian_base_model1")
model1 = AutoModelForSeq2SeqLM.from_pretrained("/code_generator/distilroberta_marian_base_model1").to(device)


# Load the second model and tokenizer
model2_tokenizer = AutoTokenizer.from_pretrained("/code_generator/fine_tuned_modelT5", use_fast=False)
model2 = AutoModelForSeq2SeqLM.from_pretrained("/code_generator/fine_tuned_modelT5").to(device)


def generate_code_model1(NL_list, max_length=1024):
    if not model1_tokenizer or not model1:
        return None  # Handle cases where model/tokenizer loading failed

    output_codes = []
    for NL in NL_list:
        # Tokenize the input
        inputs = model1_tokenizer([NL], padding="max_length", truncation=True, max_length=512, return_tensors="pt")
        input_ids = inputs.input_ids.to(device)
        attention_mask = inputs.attention_mask.to(device)

        # Generate code
        try:
            outputs = model1.generate(
                input_ids,
                attention_mask=attention_mask,
                max_length=max_length,  # Adjust the max length of the generated code
                num_beams=4,  # Use beam search for better results
                early_stopping=True
            )
            # Decode the output
            output_code = model1_tokenizer.batch_decode(outputs, skip_special_tokens=True)
            output_codes.append(output_code[0] if output_code else None)
        except Exception as e:
            print(f"Error generating code: {e}")
            output_codes.append(None)

    return output_codes


def generate_code_model2(actions, max_new_tokens=200):
    if not model2_tokenizer or not model2:
        raise ValueError("Model or tokenizer for model2 not loaded properly")
    
    # Tokenize input actions
    inputs = model2_tokenizer(actions, return_tensors='pt', padding=True, truncation=True)
    
    # Generate code
    with torch.no_grad():
        outputs = model2.generate(**inputs, max_new_tokens=max_new_tokens)
    
    # Decode outputs
    decoded_outputs = [model2_tokenizer.decode(output, skip_special_tokens=True) for output in outputs]
    
    return decoded_outputs

@csrf_exempt
def generate_codes_view(request):
    if request.method == 'POST':
        try:
            # Load JSON data from request body
            data = json.loads(request.body.decode('utf-8'))
            descriptions = data.get('descriptions', [])
            model_choice = data.get('model_choice', 'model1')  # Default to model1 if not provided
        except json.JSONDecodeError as e:
            return JsonResponse({'error': f'Invalid JSON: {str(e)}'}, status=400)

        if not descriptions:
            return JsonResponse({'error': 'No descriptions provided'}, status=400)
        
        try:
            if model_choice == 'model1' and model1_tokenizer and model1:
                output_codes = generate_code_model1(descriptions)
            elif model_choice == 'model2' and model2_tokenizer and model2:
                output_codes = generate_code_model2(descriptions)
            else:
                return JsonResponse({'error': 'Model choice invalid or model/tokenizer not loaded'}, status=500)
            
            data = {
                'descriptions': descriptions,
                'generated_codes': output_codes
            }
            return JsonResponse(data)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def handle_excel_upload(request):
    if request.method == 'POST':
        file = request.FILES['file']
        df = pd.read_excel(file)

        # Assuming 'Step Action' column exists in the file
        if 'Step Action' in df.columns:
            step_actions = df['Step Action'].dropna().tolist()
            return JsonResponse({'step_actions': step_actions})
        else:
            return JsonResponse({'error': 'Step Action column not found'}, status=400)
@csrf_exempt
def download_excel_view(request):
    if request.method == 'POST':
        try:
            descriptions = json.loads(request.POST.get('descriptions', '[]'))
            generated_codes = json.loads(request.POST.get('generated_codes', '[]'))
        except json.JSONDecodeError as e:
            return JsonResponse({'error': f'Invalid JSON: {str(e)}'}, status=400)

        if not descriptions or not generated_codes:
            return JsonResponse({'error': 'No data provided'}, status=400)

        # Create a DataFrame and save it to an Excel file
        df = pd.DataFrame({
            'Actions': descriptions,
            'Code': generated_codes
        })

        excel_file_path = 'generated_codes.xlsx'
        df.to_excel(excel_file_path, index=False)

        # Read the file and send it as an HTTP response
        with open(excel_file_path, 'rb') as excel_file:
            response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{excel_file_path}"'
            return response

    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def download_txt_view(request):
    print("Request made to download_txt_view")

    if request.method == 'POST':
        try:
            descriptions = json.loads(request.POST.get('descriptions', '[]'))
            generated_codes = json.loads(request.POST.get('generated_codes', '[]'))
        except json.JSONDecodeError as e:
            return JsonResponse({'error': f'Invalid JSON: {str(e)}'}, status=400)

        if not descriptions or not generated_codes:
            return JsonResponse({'error': 'No data provided'}, status=400)

        # Create a text file with generated codes
        text_content = '\n'.join(generated_codes)
        response = HttpResponse(text_content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="generated_codes.txt"'
        return response

    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

def index(request):
    return render(request, 'index.html')  # Assuming you have an index.html template
