from pydub import AudioSegment
import numpy as np
import array
import struct
import math

'''
    Trích rút đặc trưng
'''
def features(file):
    audio_file = readFileAudio(file)
    frames = audioFraming(audio_file)
    features = []
    for frame in frames:
        if(checkSilence(frame)):
            z = zeroCrossingRate(frame)
            ae = averageEnergy(frame)
            af = averageFrequency(frame)
            vf = frequencyVariation(frame)
            ap = averagePitch(frame)
            vp = pitchVariation(frame)
            features.append([ae, z, af, vf, ap, vp])
    return features

'''
    Sử dụng AudioSegment để đọc file âm thanh từ đường dẫn
'''
def readFileAudio(fileName):
    # Load audio file
    audio_file = AudioSegment.from_file(fileName)

    # Convert to mono channel
    audio_file = audio_file.set_channels(1)

    return audio_file

'''
    Chia file âm thanh thành các đoạn có độ dài 0.5s, mỗi đoạn cách nhau 0.25s
                
'''
def audioFraming(audio_file):
    # Set frame length and hop length in milliseconds
    frame_length = 500 #Do dai: 0.5s
    hop_length = 250 #Khoang cach giua cac frame: 0.25s

    # Calculate number of frames
    num_frames = int(len(audio_file) / hop_length) - 1

    # Initialize empty list for frames
    frames = []

    # Cut audio file into frames
    for i in range(num_frames):
        start_time = i * hop_length
        end_time = start_time + frame_length
        frame = audio_file[start_time:end_time]
        frames.append(frame)
    
    return frames

'''
    Kiểm tra đoạn âm thanh có phải im lặng ko
    Nếu >= 80% đoạn âm thanh im lặng thì đoạn âm thanh đó im lặng
'''
def checkSilence(audio):
    samples = np.array(audio.get_array_of_samples())

    # ngưỡng độ lớn tạm dừng (silence threshold)
    threshold = 280

    # Tính toán số mẫu (samples) trong file âm thanh có độ lớn dưới ngưỡng độ lớn tạm dừng
    silence_samples = len(np.where(abs(samples) < threshold)[0]) 

    # Tính toán tỷ lệ âm lặng (silence ratio) của file âm thanh
    silence_ratio = silence_samples / len(samples)
    if(silence_ratio >= 0.8):
        return False
    return True

'''
    Tính tốc độ qua điểm 0
'''
def zeroCrossingRate(audio):
    # Extract samples from audio file
    samples = np.array(audio.get_array_of_samples())

    # Calculate zero crossing rate
    zero_crossings = np.where(np.diff(np.sign(samples)))[0]
    zero_crossing_rate = len(zero_crossings) / len(samples)

    # Return zero crossing rate
    return zero_crossing_rate

'''
    Tính năng lượng trung bình
'''
# def averageEnergy(audio):
#     # Calculate RMS energy
#     rms_energy = audio.rms

#     # Return RMS energy
#     return rms_energy

def _get_samples(cp, size):
    for i in range(22050):
        yield _get_sample(cp, size, i)

# Lấy mẫu từ dữ liệu thô


def _get_sample(cp, size, i):
    global z
    start = i * size
    end = start + size
    return struct.unpack_from('h', cp[start:end])[0]


def rms(cp, size):
    sample_count = 22050
    sum_squares = sum(sample**2 for sample in _get_samples(cp, size))
    return int(math.sqrt(sum_squares / sample_count))


def averageEnergy(audio):
    # Calculate RMS energy
    # rms_energy = audio.rms
    rms_energy = rms(audio._data, 2)

    # Return RMS energy
    return rms_energy


'''
    Tính tần số trung bình
'''
def averageFrequency(audio):
    # chuyển đổi tín hiệu âm thanh sang miền tần số
    samples = np.array(audio.get_array_of_samples())
    frequencies = np.fft.fftfreq(len(samples), d=1.0/audio.frame_rate)
    spectral = np.fft.fft(samples)

    # tính trung bình các tần số
    avg_freq = np.abs(spectral).dot(np.abs(frequencies)) / np.sum(np.abs(spectral))

    return avg_freq

'''
    Tính độ biến thiên tần số
'''
def frequencyVariation(audio):
    # chuyển đổi tín hiệu âm thanh sang miền tần số
    samples = np.array(audio.get_array_of_samples())
    frequencies = np.fft.fftfreq(len(samples), d=1.0/audio.frame_rate)
    spectral = np.fft.fft(samples)

    # tính độ biến thiên tần số
    diff_freq = np.abs(np.diff(spectral))
    mean_diff_freq = np.mean(diff_freq, axis=0)
    return mean_diff_freq

'''
    Tính cao độ trung bình
'''
def averagePitch(audio):
    # chuyển đổi tín hiệu âm thanh sang mảng numpy
    samples = np.array(audio.get_array_of_samples())

    # tính phổ tín hiệu âm thanh
    spectrum = np.fft.fft(samples)

    # tính giá trị tần số cơ bản (fundamental frequency)
    freqs = np.fft.fftfreq(len(samples), d=1.0/audio.frame_rate)     # d=1.0/audio.frame_rate là khoảng thời gian giữa các mẫu (nghịch đảo của tốc độ lấy mẫu)
     # Tìm các vị trí trong mảng freqs mà giá trị tần số tại đó lớn hơn 0
    pos_mask = np.where(freqs > 0)
     # Giữ lại các tần số dương trong mảng freqs
    freqs = freqs[pos_mask]
     # Lọc phổ tương ứng với các tần số dương
    spectrum = spectrum[pos_mask]
    # Tần số cơ bản là tần số tại vị trí có biên độ lớn nhất
    peak = np.argmax(np.abs(spectrum))
    fundamental_freq = freqs[peak]

    # tính pitch từ giá trị tần số cơ bản
    pitch = 0.0
    if fundamental_freq > 0:
        pitch = audio.frame_rate / fundamental_freq
    return pitch

'''
    Tính độ biến thiên cao độ
'''
def pitchVariation(audio):
    # chuyển đổi tín hiệu âm thanh sang mảng numpy
    samples = np.array(audio.get_array_of_samples())

    # tính giá trị tần số cơ bản (fundamental frequency) trong các khung thời gian nhỏ
    window_size = int(audio.frame_rate / 100.0)  # kích thước cửa sổ trượt
    hop_size = window_size // 2  # khoảng cách giữa các cửa sổ

    fundamental_freqs = []

    for i in range(0, len(samples) - window_size, hop_size):
        window = samples[i:i+window_size]
        spectrum = np.fft.fft(window)
        freqs = np.fft.fftfreq(len(window), d=1.0/audio.frame_rate)
        pos_mask = np.where(freqs > 0)
        spectrum = spectrum[pos_mask]
        freqs = freqs[pos_mask]
        peak = np.argmax(np.abs(spectrum))
        fundamental_freq = freqs[peak]
        fundamental_freqs.append(fundamental_freq)

    # tính độ biến thiên pitch
    diff_freqs = np.abs(np.diff(fundamental_freqs))
    mean_diff_freqs = np.mean(diff_freqs)
    return mean_diff_freqs

