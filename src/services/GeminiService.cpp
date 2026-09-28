#include "services/GeminiService.h"

#include <QObject>
#include <QCoreApplication>
#include <QDir>
#include <QByteArray>
#include <QFile>
#include <QRegularExpression>

#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonParseError>

#include <QtNetwork/QNetworkAccessManager>
#include <QtNetwork/QNetworkRequest>
#include <QtNetwork/QNetworkReply>

GeminiService::GeminiService(QObject* parent)
    : QObject(parent), m_currentReply(nullptr)
{
}

GeminiService::~GeminiService()
{
    if (m_currentReply) {
        m_currentReply->deleteLater();
    }
}

static QString getEnvValue(const QString& keyName)
{
    QByteArray envVal = qgetenv(keyName.toUtf8().constData());
    if (!envVal.isEmpty()) {
        return QString::fromUtf8(envVal).trimmed();
    }

    const QString envFilePath = QDir::currentPath() + QDir::separator() + ".env";
    QFile envFile(envFilePath);
    if (envFile.open(QIODevice::ReadOnly | QIODevice::Text)) {
        while (!envFile.atEnd()) {
            const QString line = QString::fromUtf8(envFile.readLine()).trimmed();
            if (line.startsWith(keyName + "=")) {
                return line.mid(keyName.length() + 1).trimmed();
            }
        }
    }
    return QString();
}

QString GeminiService::apiKey()
{
    QString key = getEnvValue("OPENAI_API_KEY");
    if (!key.isEmpty()) {
        return key;
    }
    return getEnvValue("GEMINI_API_KEY");
}

static bool isOpenAiKey(const QString& key)
{
    return key.startsWith("sk-") || !getEnvValue("OPENAI_API_KEY").isEmpty();
}

void GeminiService::fetchWordInfo(const QString& word)
{
    const QString cleanWord = sanitizedWord(word);
    if (cleanWord.isEmpty()) {
        emit wordInfoError("Please enter a valid word.");
        return;
    }

    const QString key = apiKey();
    if (key.isEmpty()) {
        emit wordInfoError("API key is not configured. Please set OPENAI_API_KEY in .env");
        return;
    }

    m_pendingWord = cleanWord;

    if (isOpenAiKey(key)) {
        QUrl url(QStringLiteral("https://api.openai.com/v1/chat/completions"));
        QNetworkRequest request(url);
        request.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");
        request.setRawHeader("Authorization", QString("Bearer %1").arg(key).toUtf8());
        request.setAttribute(QNetworkRequest::RedirectPolicyAttribute, QNetworkRequest::NoLessSafeRedirectPolicy);

        QJsonObject requestBody;
        requestBody["model"] = "gpt-4o-mini";
        requestBody["temperature"] = 0.2;

        QJsonArray messages;
        QJsonObject sysMsg;
        sysMsg["role"] = "system";
        sysMsg["content"] = "You are a professional dictionary assistant. Always respond with only raw JSON (no markdown formatting, no code fences).";
        messages.append(sysMsg);

        QJsonObject userMsg;
        userMsg["role"] = "user";
        userMsg["content"] = buildPrompt(cleanWord);
        messages.append(userMsg);

        requestBody["messages"] = messages;

        QNetworkReply* reply = m_networkManager.post(request, QJsonDocument(requestBody).toJson(QJsonDocument::Compact));
        if (m_currentReply) {
            m_currentReply->deleteLater();
        }
        m_currentReply = reply;
        connect(reply, &QNetworkReply::finished, this, &GeminiService::onReplyFinished);
    } else {
        const QString urlString = QStringLiteral("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=%1").arg(key);
        QUrl url(urlString);
        QNetworkRequest request(url);
        request.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");
        request.setAttribute(QNetworkRequest::RedirectPolicyAttribute, QNetworkRequest::NoLessSafeRedirectPolicy);

        QNetworkReply* reply = m_networkManager.post(request, QJsonDocument(buildRequestBody(cleanWord)).toJson(QJsonDocument::Compact));
        if (m_currentReply) {
            m_currentReply->deleteLater();
        }
        m_currentReply = reply;
        connect(reply, &QNetworkReply::finished, this, &GeminiService::onReplyFinished);
    }
}

void GeminiService::onReplyFinished()
{
    if (!m_currentReply) {
        return;
    }

    const QByteArray response = m_currentReply->readAll();
    const QNetworkReply::NetworkError error = m_currentReply->error();
    m_currentReply->deleteLater();
    m_currentReply = nullptr;

    if (error != QNetworkReply::NoError) {
        // Try extracting API error message if available
        QJsonParseError errJson;
        QJsonDocument doc = QJsonDocument::fromJson(response, &errJson);
        if (!doc.isNull() && doc.isObject()) {
            QJsonObject obj = doc.object();
            if (obj.contains("error")) {
                QJsonObject errObj = obj.value("error").toObject();
                QString msg = errObj.value("message").toString();
                if (!msg.isEmpty()) {
                    emit wordInfoError(QString("API Error: %1").arg(msg));
                    return;
                }
            }
        }
        emit wordInfoError("Unable to reach the dictionary service. Please check your API key and connection.");
        return;
    }

    if (response.isEmpty()) {
        emit wordInfoError("We couldn't find information for this word. Please try again.");
        return;
    }

    try {
        Word word = parseResponse(response);
        if (!word.isValid()) {
            emit wordInfoError(QString("We couldn't find information for \"%1\". Please check the spelling and try again.").arg(m_pendingWord));
            return;
        }
        emit wordInfoReady(word);
    } catch (...) {
        emit wordInfoError("The dictionary service returned invalid data. Please try again.");
    }
}

QJsonObject GeminiService::buildRequestBody(const QString& word) const
{
    QJsonObject request;
    QJsonObject contents;
    QJsonArray parts;

    const QString prompt = buildPrompt(word);
    QJsonObject textPart;
    textPart["text"] = prompt;
    parts.append(textPart);
    contents["parts"] = parts;
    request["contents"] = QJsonArray{contents};

    QJsonObject generationConfig;
    generationConfig["temperature"] = 0.2;
    request["generationConfig"] = generationConfig;
    return request;
}

QString GeminiService::buildPrompt(const QString& word) const
{
    return QString(
        "Return only valid JSON in English with this exact structure for the word '%1'. "
        "Do not include markdown fences, backticks, or commentary. "
        "Fields: word, pronunciation, part_of_speech, definitions, synonyms, antonyms, examples, related_words. "
        "Use a JSON object. Make definitions an array of strings, synonyms an array of strings, antonyms an array of strings, examples an array of strings, and related_words an array of strings. "
        "If the word is unknown, return {\"word\":\"%1\",\"pronunciation\":\"\",\"part_of_speech\":\"\",\"definitions\":[],\"synonyms\":[],\"antonyms\":[],\"examples\":[],\"related_words\":[]} ")
        .arg(word);
}

Word GeminiService::parseResponse(const QByteArray& data) const
{
    QJsonParseError parseError;
    const QJsonDocument doc = QJsonDocument::fromJson(data, &parseError);
    if (parseError.error != QJsonParseError::NoError || !doc.isObject()) {
        return Word();
    }

    const QJsonObject root = doc.object();

    // 1. Handle OpenAI chat completion response format
    if (root.contains("choices")) {
        const QJsonArray choices = root.value("choices").toArray();
        if (!choices.isEmpty()) {
            const QJsonObject firstChoice = choices.at(0).toObject();
            const QJsonObject message = firstChoice.value("message").toObject();
            QString content = message.value("content").toString().trimmed();

            // Strip possible markdown json fences
            if (content.startsWith("```json")) {
                content = content.mid(7);
            } else if (content.startsWith("```")) {
                content = content.mid(3);
            }
            if (content.endsWith("```")) {
                content.chop(3);
            }
            content = content.trimmed();

            int start = content.indexOf('{');
            int end = content.lastIndexOf('}');
            if (start >= 0 && end > start) {
                content = content.mid(start, end - start + 1);
            }

            const QJsonDocument jsonDoc = QJsonDocument::fromJson(content.toUtf8(), &parseError);
            if (parseError.error == QJsonParseError::NoError && jsonDoc.isObject()) {
                return Word::fromJsonObject(jsonDoc.object());
            }
        }
    }

    // 2. Handle Gemini candidates format
    const QJsonValue candidates = root.value("candidates");
    if (candidates.isArray() && !candidates.toArray().isEmpty()) {
        const QJsonValue firstCandidate = candidates.toArray().at(0);
        if (firstCandidate.isObject()) {
            const QJsonObject candidateObject = firstCandidate.toObject();
            const QJsonValue contentValue = candidateObject.value("content");
            if (contentValue.isObject()) {
                const QJsonObject contentObject = contentValue.toObject();
                const QJsonValue parts = contentObject.value("parts");
                if (parts.isArray() && !parts.toArray().isEmpty()) {
                    const QJsonValue firstPart = parts.toArray().at(0);
                    if (firstPart.isObject()) {
                        const QJsonObject partObject = firstPart.toObject();
                        const QString text = partObject.value("text").toString();
                        if (!text.isEmpty()) {
                            QString cleanText = text;
                            int start = cleanText.indexOf('{');
                            int end = cleanText.lastIndexOf('}');
                            if (start >= 0 && end > start) {
                                cleanText = cleanText.mid(start, end - start + 1);
                            }

                            const QJsonDocument jsonDoc = QJsonDocument::fromJson(cleanText.toUtf8(), &parseError);
                            if (parseError.error == QJsonParseError::NoError && jsonDoc.isObject()) {
                                return Word::fromJsonObject(jsonDoc.object());
                            }
                        }
                    }
                }
            }
        }
    }

    return Word();
}

QString GeminiService::sanitizedWord(const QString& rawWord)
{
    QString value = rawWord.trimmed();
    value.replace(QRegularExpression("\\s+"), " ");
    return value;
}
