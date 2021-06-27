import abc

from deeppavlov import train_model, build_model, configs
from deeppavlov.core.common.file import read_json

from nltk.corpus import stopwords


class FallbackMessageAdviser:
    def __init__(self, threshold: float, fallback_file="fallback.md"):
        if threshold > 1.0:
            threshold = 1
        if threshold < 0.0:
            threshold = 0
        self.threshold = threshold
        self.fallback_message = fallback_file

    def message_or_fallback(self, probability: float, message: str):
        # return message
        if probability >= self.threshold:
            return message
        else:
            return self.fallback_message


class ChatBot:

    def __init__(
            self,
            config_path: str = "config/tfidf_vectorizer_ruwiki-v3.json",
            fallback: FallbackMessageAdviser = FallbackMessageAdviser(0.6),
    ):
        self._fallback = fallback
        stop_words = stopwords.words('russian')
        stop_words.extend(['что', 'это', 'так', 'вот', 'быть', 'как', 'в', '—', '–', 'к', 'на', '...'])

        model_config = read_json(config_path)
        self._model = train_model(model_config)  # или build_model(model_config)
        # result = model("меня задержали")

    def ask(self, question: str):
        answers, probability = self._model([question])
        message = self._fallback.message_or_fallback(max(probability[0]), answers[0])
        return message
        #valid = self._check_similarity(probability[0], self._fallback.threshold)
        #if valid:
        #    return answers[0], True
        #else:
        #    return self._fallback.fallback_message, True

    @staticmethod
    def normalize_text(self):
        pass
    @staticmethod
    def _check_similarity(arr: list, threshold: float) -> bool:
        max_value = max(arr)
        print(max_value)
        if max_value < threshold:
            return False
        else:
            return True
