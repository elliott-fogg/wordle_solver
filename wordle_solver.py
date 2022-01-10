import random
import statistics as stats

class wordle_guess_info():
    def __init__(self, green={}, yellow={}, red=set(), bad_duplicates={}, good_duplicates={}):
        self.green = green
        self.yellow = yellow
        self.red = red
        self.bad_duplicates = bad_duplicates
        self.good_duplicates = good_duplicates
        
    def __add__(self, info):
        if info == None:
            return self
        elif type(info) != type(self):
            raise Exception(f"Can only add wordle_guess_info to similar objects, not to type {type(info)}.")
        
        green = {**self.green, **info.green}
        red = self.red.union(info.red)
        bad_duplicates = {**self.bad_duplicates, **info.bad_duplicates}
        
        # Good duplicate propogation        
        good_duplicates = self.good_duplicates
        for key in info.good_duplicates:
            if key in good_duplicates:
                good_duplicates[key] = max(self.good_duplicates[key],
                                           info.good_duplicates[key])
            else:
                good_duplicates[key] = info.good_duplicates[key]
        
        # Yellow propogation
        yellow = {}
        for d in (self.yellow, info.yellow):
            for char in d:
                if char not in yellow:
                    yellow[char] = set()
                yellow[char].update(d[char])
                
        return wordle_guess_info(green, yellow, red, bad_duplicates, good_duplicates)
                
    def __str__(self):
        return f"{self.green}, {self.yellow}, {self.red}, {self.bad_duplicates}, {self.good_duplicates}"


class wordle_solver():
    def __init__(self, answer=None, mode="random"):
        self.answer = answer
        with open("sgb-words.txt", "r") as f:
            self.all_words = [w for w in f.read().split("\n") if len(w) == 5]
        
        
    def guess_from_answer(self, guess, answer=None):
        green = {}
        yellow = {}
        red = set()
        bad_duplicates = {}
        good_duplicates = {}

        current_chars = []

        for i in range(5):
            q_char = guess[i]
            current_chars.append(q_char)

            if (q_char in bad_duplicates) or (q_char in red):
                # Letter already used and not present, skip
                continue

            if not q_char in answer:
                # Character is not in word
                red.add(q_char)
                continue

            if answer[i] == q_char:
                # Character is present, and in correct place
                green[i] = q_char
                continue

            # Check whether it is a duplicate letter
            guess_count = current_chars.count(q_char)
            answer_count = answer.count(q_char)
            if answer_count < guess_count:
                # Letter is a duplicate, and the subsequent one is not in answer
                bad_duplicates[q_char] = guess_count
                continue
            elif guess_count > 1:
                good_duplicates[q_char] = guess_count

            # Letter must be present in answer, but in wrong place.
            if q_char not in yellow:
                yellow[q_char] = set()
            yellow[q_char].add(i)
            continue

        return wordle_guess_info(green, yellow, red, bad_duplicates, good_duplicates)
    
    
    def guess_from_code(self, guess, code):
        green = {}
        yellow = set()
        red = set()
        bad_duplicates = {}
        good_duplicates = {}

        current_chars = []

        for i in range(len(code)):
            char = guess[i]

            if code[i] in "Gg":
                green[i] = char

            elif code[i] in "Yy":
                if char not in yellow:
                    yellow[char] = set()
                yellow[char].add(i)
                if char in current_chars:
                    good_duplicates[char] = current_chars.count(char) + 1

            elif code[i] in "Rr_":
                if char in current_chars:
                    if char not in bad_duplicates:
                        bad_duplicates[char] = current_chars.count(char) + 1

                else :
                    red.add(char)

            current_chars.append(char)

        return wordle_guess_info(green, yellow, red, bad_duplicates, good_duplicates)
    
    
    def get_word_scores(self, remaining_words, current_info=None):
        results = []
        for assumed_guess in self.all_words:
            guess_results = []
            for assumed_answer in remaining_words:
                assumed_info = self.guess_from_answer(assumed_guess, assumed_answer) + current_info
                assumed_remaining_words = self.filter_words(remaining_words, assumed_info)
                guess_results.append(len(assumed_remaining_words))

            score = stats.mean(guess_results)
            results.append( (assumed_guess, score) )
        return sorted(results, key=lambda x: x[1])
    
    
    def filter_words(self, remaining_words, info):
        return [word for word in remaining_words if self.check_word(word, info)]
                    
        
    def check_word(self, word, info):
        for i in info.green:
            if word[i] != info.green[i]:
                return False
            
        for char in info.yellow:
            for i in info.yellow[char]:
                if word[i] == char:
                    return False
                
        for char in info.red:
            if char in word:
                return False
            
        for char in info.bad_duplicates:
            if word.count(char) >= info.bad_duplicates[char]:
                return False
            
        for char in info.good_duplicates:
            if word.count(char) < info.good_duplicates[char]:
                return False
            
        return True
    
    
    def solve(self, verbose=1):
        if answer == None:
            print("No answer specified. Cannot solve.")
            return
        
        guess = "tares"
        guesses = [guess]
        info = self.guess_from_answer(guess, self.answer)
        remaining_words = self.filter_words(self.all_words, info)
        
        while len(remaining_words) > 1:
            if verbose == 2:
                print(f"Guess: {guess} - Remaining Words: {len(remaining_words)}")
            word_scores = self.get_word_scores(remaining_words, info)
            guess = word_scores[0][0]
            guesses.append(guess)
            info = self.guess_from_answer(guess, self.answer) + info
            remaining_words = self.filter_words(remaining_words, info)
            
        if verbose >= 1:
            print(f"Answer: {remaining_words[0]}")
            print(f"Guesses: {len(guesses)}")

        return len(guesses)


    def manual_guess(self, guess, mute=False):
        guess = guess.lower()

        if not mute:
            if guess not in self.all_words:
                print(f"Note: {guess} is not included in the known words of this program.")

        response = ""
        for i in range(len(guess)):
            char = guess[i]
            if char == self.answer[i]:
                response += char.upper()
            elif char not in self.answer:
                response += "-"
            else:
                if answer.count(char) > response.lower().count(char):
                    response += char
                else:
                    response += "-"
        return response

### Multiprocessing Functions ################################################
        
def check_word(word, info):
    for i in info.green:
        if word[i] != info.green[i]:
            return False
        
    for char in info.yellow:
        for i in info.yellow[char]:
            if word[i] == char:
                return False
            
    for char in info.red:
        if char in word:
            return False
        
    for char in info.bad_duplicates:
        if word.count(char) >= info.bad_duplicates[char]:
            return False
        
    for char in info.good_duplicates:
        if word.count(char) < info.good_duplicates[char]:
            return False
        
    return True


def worker_check_words(words_to_check, remaining_words, info):
    output = []
    for assumed_guess in words_to_check:
        guess_results = []
        for assumed_answer in remaining_words:
            assumed_info = guess_from_answer(assumed_guess,
                                                        assumed_answer) + info
            assumed_remaining_words = [w for w in remaining_words if 
                                                                check_word(w)]
            guess_results.append(len(assumed_remaining_words))
        score = sum(guess_results)
        output.append( (assumed_guess, score) )
    return output



if __name__ == "__main__":
    wordle_solver(sys.argv[1]).solve(verbose=2)