import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

class ApiService {
  static const baseUrl = 'http://localhost:8000';

  Future<Map<String, dynamic>> uploadImage(String filePath) async {
    final req = http.MultipartRequest('POST', Uri.parse('$baseUrl/api/upload/image'));
    req.files.add(await http.MultipartFile.fromPath('file', filePath));
    final res = await req.send();
    return jsonDecode(await res.stream.bytesToString());
  }

  Future<Map<String, dynamic>> uploadAudio(String filePath) async {
    final req = http.MultipartRequest('POST', Uri.parse('$baseUrl/api/upload/audio'));
    req.files.add(await http.MultipartFile.fromPath('file', filePath));
    final res = await req.send();
    return jsonDecode(await res.stream.bytesToString());
  }

  Future<String> generateReel({
    required String imageFilename,
    required String audioFilename,
    required String style,
    required String engine,
  }) async {
    final res = await http.post(
      Uri.parse('$baseUrl/api/generate'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'image_filename': imageFilename,
        'audio_filename': audioFilename,
        'style': style,
        'engine': engine,
      }),
    );
    final data = jsonDecode(res.body);
    return data['job_id'] as String;
  }

  Future<Map<String, dynamic>> getJobStatus(String jobId) async {
    final res = await http.get(Uri.parse('$baseUrl/api/job/$jobId'));
    return jsonDecode(res.body);
  }
}
