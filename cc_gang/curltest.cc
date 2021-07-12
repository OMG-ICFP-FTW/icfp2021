#include <iostream>
#include <curl/curl.h>
#include <string>
#include <memory>

#include <stdlib.h>

template<typename ... Args>
std::string string_format( const std::string& format, Args ... args )
{
  int size_s = std::snprintf( nullptr, 0, format.c_str(), args ... ) + 1; // Extra space for '\0'
  if( size_s <= 0 ){ throw std::runtime_error( "Error during formatting." ); }
  auto size = static_cast<size_t>( size_s );
  auto buf = std::make_unique<char[]>( size );
  std::snprintf( buf.get(), size, format.c_str(), args ... );
  return std::string( buf.get(), buf.get() + size - 1 ); // We don't want the '\0' inside
}

size_t writeFunction(void *ptr, size_t size, size_t nmemb, std::string* data) {
    data->append((char*) ptr, size * nmemb);
    return size * nmemb;
}

std::string GetProblem(int problem_id) {
  std::string response_string;
  auto curl = curl_easy_init();
  if (curl) {
    auto get_url = string_format("https://poses.live/api/problems/%d", problem_id);
    curl_easy_setopt(curl, CURLOPT_URL, get_url.c_str());

    auto auth_header = string_format("Authorization: Bearer %s", std::getenv("STEEZYKEY"));
    struct curl_slist* headers = NULL;
    headers = curl_slist_append(headers, auth_header.c_str());
    headers = curl_slist_append(headers, "Content-Type: application/json");
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);

    // curl_easy_setopt(curl, CURLOPT_NOPROGRESS, 1L);
    // curl_easy_setopt(curl, CURLOPT_USERPWD, "user:pass");
    // curl_easy_setopt(curl, CURLOPT_USERAGENT, "curl/7.42.0");
    // curl_easy_setopt(curl, CURLOPT_MAXREDIRS, 50L);
    // curl_easy_setopt(curl, CURLOPT_TCP_KEEPALIVE, 1L);

    std::string header_string;
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, writeFunction);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response_string);
    curl_easy_setopt(curl, CURLOPT_HEADERDATA, &header_string);

    char* url;
    long response_code;
    double elapsed;
    curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &response_code);
    curl_easy_getinfo(curl, CURLINFO_TOTAL_TIME, &elapsed);
    curl_easy_getinfo(curl, CURLINFO_EFFECTIVE_URL, &url);

    curl_easy_perform(curl);
    curl_easy_cleanup(curl);
    curl = NULL;
  }
  return response_string;
}

std::string SubmitProblem(int problem_id, const std::string& data) {
  std::string response_string;
  auto curl = curl_easy_init();
  if (curl) {
    auto get_url = string_format("https://poses.live/api/problems/%d/solutions", problem_id);
    curl_easy_setopt(curl, CURLOPT_URL, get_url.c_str());

    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, data.c_str());

    auto auth_header = string_format("Authorization: Bearer %s", std::getenv("STEEZYKEY"));
    struct curl_slist* headers = NULL;
    headers = curl_slist_append(headers, auth_header.c_str());
    headers = curl_slist_append(headers, "Content-Type: application/json");
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);

    // curl_easy_setopt(curl, CURLOPT_NOPROGRESS, 1L);
    // curl_easy_setopt(curl, CURLOPT_USERPWD, "user:pass");
    // curl_easy_setopt(curl, CURLOPT_USERAGENT, "curl/7.42.0");
    // curl_easy_setopt(curl, CURLOPT_MAXREDIRS, 50L);
    // curl_easy_setopt(curl, CURLOPT_TCP_KEEPALIVE, 1L);

    std::string header_string;
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, writeFunction);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response_string);
    curl_easy_setopt(curl, CURLOPT_HEADERDATA, &header_string);

    char* url;
    long response_code;
    double elapsed;
    curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &response_code);
    curl_easy_getinfo(curl, CURLINFO_TOTAL_TIME, &elapsed);
    curl_easy_getinfo(curl, CURLINFO_EFFECTIVE_URL, &url);

    curl_easy_perform(curl);
    curl_easy_cleanup(curl);
    curl = NULL;
  }
  return response_string;
}

int main(int argc, char** argv) {
  curl_global_init(CURL_GLOBAL_DEFAULT);
  std::cout << "GET" << std::endl;
  std::cout << GetProblem(1) << std::endl;
  std::cout << "POST" << std::endl;
  std::cout << SubmitProblem(132, "ayylmao") << std::endl;
}
