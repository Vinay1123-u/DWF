cmake_minimum_required(VERSION 3.16)
project(DictionaryWordFinder VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

find_package(Qt6 REQUIRED COMPONENTS Widgets Sql Network)

add_executable(DictionaryWordFinder
    src/main.cpp
    src/models/User.cpp
    src/models/Word.cpp
    src/models/SearchHistory.cpp
    src/models/SavedWord.cpp
    src/database/DatabaseManager.cpp
    src/utils/PasswordHasher.cpp
    src/utils/Validators.cpp
    src/services/AuthenticationService.cpp
    src/services/GeminiService.cpp
    src/ui/LoginWindow.cpp
    src/ui/RegisterWindow.cpp
    src/ui/MainWindow.cpp
    src/ui/DashboardWidget.cpp
    src/ui/SearchWidget.cpp
    src/ui/SavedWordsWidget.cpp
    src/ui/HistoryWidget.cpp
    src/ui/ProfileWidget.cpp
    src/ui/SettingsWidget.cpp
    resources/resources.qrc
)

target_include_directories(DictionaryWordFinder PRIVATE
    ${CMAKE_SOURCE_DIR}/src
    ${CMAKE_SOURCE_DIR}/src/database
    ${CMAKE_SOURCE_DIR}/src/models
    ${CMAKE_SOURCE_DIR}/src/services
    ${CMAKE_SOURCE_DIR}/src/ui
    ${CMAKE_SOURCE_DIR}/src/utils
)

target_link_libraries(DictionaryWordFinder PRIVATE Qt6::Widgets Qt6::Sql Qt6::Network)

set_target_properties(DictionaryWordFinder PROPERTIES
    WIN32_EXECUTABLE OFF
)
