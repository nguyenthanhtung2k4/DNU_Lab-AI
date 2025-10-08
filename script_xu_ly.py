import pandas as pd
import os
import re
import sys

# ==============================================================================
# >>> CÀI ĐẶT CẦN THIẾT <<<
# ==============================================================================

# Số lượng file ghi âm cần xử lý
NUM_FILES_TO_RENAME = 306

# >>> 1. ĐƯỜNG DẪN ĐẾN FILE CSV <<<
# Ví dụ trên Windows: 'C:\\Users\\TenBan\\Documents\\text_audi.csv'
# Ví dụ trên macOS/Linux: '/Users/TenBan/Documents/text_audi.csv'
csv_file_path = './text_audio.csv' 

# >>> 2. ĐƯỜNG DẪN ĐẾN FOLDER CHỨA FILE GHI ÂM <<<
# Ví dụ trên Windows: 'C:\\Users\\YourName\\Documents\\Recordings'
# Ví dụ trên macOS/Linux: '/Users/YourName/Documents/Recordings'
audio_folder_path = './audio'


# ==============================================================================
# HÀM 1: ĐỔI TÊN FILE VẬT LÝ TRONG THƯ MỤC
# ==============================================================================
def rename_audio_files(path, count):
    """
    Đổi tên các file từ 'Recording (X).wav' thành 'audioX-Tung.wav' trong folder.
    Giả định file ghi âm có đuôi là .wav. Nếu là đuôi khác, cần sửa regex.
    """
    print(f"\n--- BẮT ĐẦU ĐỔI TÊN {count} FILE GHI ÂM TRONG FOLDER ---")
    
    if not os.path.isdir(path):
        print(f"Lỗi: Đường dẫn thư mục ghi âm không hợp lệ hoặc không tồn tại: {path}")
        return False
        
    files_renamed_count = 0
    
    for filename in os.listdir(path):
        # Tìm kiếm tên file cũ: "Recording (số)"
        # Sửa regex nếu đuôi file khác .wav (ví dụ: r'^Recording \((\d+)\)\.mp3$')
        match = re.match(r'^Recording \((\d+)\)\.wav$', filename)

        if match:
            stt = int(match.group(1))
            
            if 1 <= stt <= count:
                new_name = f'audio{stt}-Tung.wav'
                old_file = os.path.join(path, filename)
                new_file = os.path.join(path, new_name)
                
                try:
                    os.rename(old_file, new_file)
                    # In ra 10 file đầu để kiểm tra
                    if files_renamed_count < 10 or stt == count:
                        print(f'Đã đổi tên: "{filename}" -> "{new_name}"')
                    files_renamed_count += 1
                except Exception as e:
                    print(f'Lỗi khi đổi tên file {filename}: {e}')

    if files_renamed_count > 0:
        print(f"Hoàn tất đổi tên! Tổng cộng {files_renamed_count} file đã được đổi tên.")
    else:
        print("Không tìm thấy file nào khớp với định dạng 'Recording (X).wav' trong thư mục.")
        
    return True

# ==============================================================================
# HÀM 2: CẬP NHẬT FILE CSV
# ==============================================================================
def update_csv_file(path, count):
    """
    Đổi tên cột 'stt' thành 'file_name' và cập nhật giá trị cho 306 dòng đầu tiên.
    """
    print("\n--- BẮT ĐẦU XỬ LÝ VÀ CẬP NHẬT FILE CSV ---")
    
    try:
        # Đọc file CSV
        df = pd.read_csv(path, encoding='utf-8')
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file CSV tại đường dẫn {path}.")
        return

    # 1. Đổi tên cột 'stt' thành 'file_name'
    if 'stt' in df.columns:
        df.rename(columns={'stt': 'file_name'}, inplace=True)
    else:
        print("Cảnh báo: Không tìm thấy cột 'stt' trong file CSV. Không thể đổi tên cột.")
        return

    # 2. Cập nhật giá trị trong cột 'file_name' (cho 306 dòng đầu)
    
    # Giới hạn số dòng cần cập nhật (306 dòng đầu tiên)
    rows_to_update = min(count, len(df))
    
    # Tạo Series chứa tên file mới
    file_names_series = pd.Series(
        [f'audio{i}-Tung.wav' for i in range(1, rows_to_update + 1)],
        index=df.index[:rows_to_update] 
    )

    # Gán giá trị mới cho các dòng cần cập nhật
    df.loc[:rows_to_update - 1, 'file_name'] = file_names_series

    # >>> LƯU FILE ĐÃ CẬP NHẬT <<<
    # Lưu vào file mới để không ghi đè lên file gốc nếu có lỗi
    output_file_path = path.replace('.csv', '_updated.csv')
    df.to_csv(output_file_path, index=False, encoding='utf-8')
    
    print("Hoàn tất xử lý CSV!")
    print(f"Đã lưu file CSV đã cập nhật tại: {output_file_path}")
    print("\nKiểm tra dữ liệu (Dòng 306 và 307):")
    
    # Hiển thị kiểm tra dòng giới hạn 306 và 307
    index_306 = df[df['file_name'] == 'audio306-Tung.wav'].index
    if not index_306.empty:
        index_306 = index_306[0]
        
        print("\n--- Dòng 306 ---")
        print(df.loc[index_306:index_306].to_markdown(index=False))
        
        # Hiển thị dòng 307 (dòng tiếp theo)
        if index_306 + 1 < len(df):
            print("\n--- Dòng 307 (Giữ nguyên số) ---")
            print(df.loc[index_306 + 1:index_306 + 1].to_markdown(index=False))

# ==============================================================================
# CHẠY CHƯƠNG TRÌNH CHÍNH
# ==============================================================================
if __name__ == '__main__':
    
    # Kiểm tra và chạy đổi tên file vật lý
    rename_success = rename_audio_files(audio_folder_path, NUM_FILES_TO_RENAME)
    
    # Chỉ xử lý CSV nếu việc đổi tên file vật lý không bị lỗi đường dẫn
    if rename_success:
        update_csv_file(csv_file_path, NUM_FILES_TO_RENAME)