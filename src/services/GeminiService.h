#pragma once

#include <QObject>
#include <QNetworkAccessManager>
#include <QNetworkReply>
#include <QUrl>

#include "models/Word.h"

class GeminiService : public QObject
{
    Q_OBJECT
public:
    explicit GeminiService(QObject* parent = nullptr);
    ~GeminiService();

    void fetchWordInfo(const QString& word);
    static QString apiKey();

signals:
    void wordInfoReady(const Word& word);
    void wordInfoError(const QString& message);

private slots:
    void onReplyFinished();

private:
    QNetworkAccessManager m_networkManager;
    QNetworkReply* m_currentReply;
    QString m_pendingWord;

    QJsonObject buildRequestBody(const QString& word) const;
    QString buildPrompt(const QString& word) const;
    Word parseResponse(const QByteArray& data) const;
    static QString sanitizedWord(const QString& rawWord);
};
