#pragma once

#include <QString>
#include <QStringList>
#include <QJsonObject>

class Word
{
public:
    Word();
    Word(const QString& word, const QString& pronunciation = QString(),
         const QString& partOfSpeech = QString(), const QStringList& definitions = QStringList(),
         const QStringList& synonyms = QStringList(), const QStringList& antonyms = QStringList(),
         const QStringList& examples = QStringList(), const QStringList& relatedWords = QStringList());

    QString word() const;
    QString pronunciation() const;
    QString partOfSpeech() const;
    QStringList definitions() const;
    QStringList synonyms() const;
    QStringList antonyms() const;
    QStringList examples() const;
    QStringList relatedWords() const;

    void setWord(const QString& word);
    void setPronunciation(const QString& pronunciation);
    void setPartOfSpeech(const QString& partOfSpeech);
    void setDefinitions(const QStringList& definitions);
    void setSynonyms(const QStringList& synonyms);
    void setAntonyms(const QStringList& antonyms);
    void setExamples(const QStringList& examples);
    void setRelatedWords(const QStringList& relatedWords);

    bool isValid() const;
    QJsonObject toJsonObject() const;
    static Word fromJsonObject(const QJsonObject& object);

private:
    QString m_word;
    QString m_pronunciation;
    QString m_partOfSpeech;
    QStringList m_definitions;
    QStringList m_synonyms;
    QStringList m_antonyms;
    QStringList m_examples;
    QStringList m_relatedWords;
};
