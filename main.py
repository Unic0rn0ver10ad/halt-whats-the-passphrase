import pp_utils

if __name__ == "__main__":
  # pp_utils.convert_dicelist_to_dictionary('eff_large_wordlist.txt')
  # print(pp_utils.generate_wordlist_from_dictionary('dictionaries/test.txt'))
  # word_list = pp_utils.generate_wordlist_from_dictionary('test.txt')
  # print(f'word_list: {word_list}')
  # filtered_list = pp_utils.filter_word_list(word_list, 4, 9)
  # pp_utils.save_wordlist_as_dictionary(filtered_list, 'test_filtered.txt')
  # new_word_list = pp_utils.generate_wordlist_from_dictionary('test_filtered.txt')
  # print(f'new_word_list: {new_word_list}')
  # words_dict = pp_utils.generate_wordlength_dict(new_word_list)
  # print(f'words_dict: {words_dict}')
  # pp_utils.process_raw_dictionary('hwtp_short_test.txt', 4, 9)
  # pp_utils.process_raw_dictionary('eff_short_wordlist_2_0.txt', 4, 9, True)
  # print(pp_utils.convert_dicelist_to_dictionary('hwtp_short_test_3.txt'))
  pp_utils.process_all_dictionaries(4, 9)
  