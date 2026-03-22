import os
import shutil

def finalize_copy():
    src_base = r'C:\Users\pietr\Downloads\arte_heavy_temp'
    dst_base = r'I:\Meu Drive\GoogleAI\arte_heavy'
    
    if not os.path.exists(src_base):
        print(f"Erro: Origem {src_base} não existe!")
        return

    # Categories to copy
    categories = [d for d in os.listdir(src_base) if os.path.isdir(os.path.join(src_base, d))]
    
    for cat in categories:
        src_dir = os.path.join(src_base, cat)
        dst_dir = os.path.join(dst_base, cat)
        
        # Ensure destination is a directory
        if os.path.exists(dst_dir) and not os.path.isdir(dst_dir):
            print(f"Removendo arquivo que deveria ser pasta: {dst_dir}")
            os.remove(dst_dir)
            
        if not os.path.exists(dst_dir):
            print(f"Criando pasta no Drive: {dst_dir}")
            os.makedirs(dst_dir, exist_ok=True)
            
        for file in os.listdir(src_dir):
            src_file = os.path.join(src_dir, file)
            dst_file = os.path.join(dst_dir, file)
            
            print(f"Copiando {file} para {dst_dir}")
            try:
                shutil.copy2(src_file, dst_file)
                print(f"Sucesso: {dst_file}")
            except Exception as e:
                print(f"Erro ao copiar {file}: {e}")

if __name__ == "__main__":
    finalize_copy()
